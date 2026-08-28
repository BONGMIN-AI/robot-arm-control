"""Inverse kinematics for the calibrated robot-arm position model.

This module only computes servo targets; it never communicates with hardware.
J4 (tool roll) and J5 (gripper) do not affect the XYZ position and are kept at
their current values.
"""

import argparse
import math
from dataclasses import dataclass

from dh_calculator import B0, H0, L1, L2, L3, L4, robot_pose
from joint_config import JOINT_LIMITS, SERVO_CENTER_DEG


POSITION_JOINTS = ("J0", "J1", "J2", "J3")
DEFAULT_CURRENT = (150.0, 150.0, 150.0, 150.0, 150.0, 150.0)
TOOL_LENGTH = L3 + L4


class InverseKinematicsError(ValueError):
    """Raised when no safe joint solution exists for a target."""


@dataclass(frozen=True)
class IKSolution:
    servo_angles: tuple[float, float, float, float, float, float]
    tool_pitch_deg: float
    position_error_mm: float
    elbow: str


def _within_limit(joint_name, servo_angle, tolerance=1e-9):
    low, high = JOINT_LIMITS[joint_name]
    return low - tolerance <= servo_angle <= high + tolerance


def _angle_distance_squared(angles, current):
    # Normalize by each joint's allowed travel so one wide-range joint does not
    # dominate selection of the solution nearest to the current pose.
    total = 0.0
    for name, angle, present in zip(POSITION_JOINTS, angles, current):
        low, high = JOINT_LIMITS[name]
        total += ((angle - present) / (high - low)) ** 2
    return total


def _pitch_candidates(tool_pitch_deg, step_deg):
    if tool_pitch_deg is not None:
        return [float(tool_pitch_deg)]
    if step_deg <= 0:
        raise ValueError("pitch_step_deg must be greater than zero")

    # tool pitch is q1 + q2 + q3. Search every orientation permitted by the
    # configured J1-J3 limits; XYZ alone leaves this orientation unconstrained.
    minimum = sum(JOINT_LIMITS[name][0] - SERVO_CENTER_DEG for name in ("J1", "J2", "J3"))
    maximum = sum(JOINT_LIMITS[name][1] - SERVO_CENTER_DEG for name in ("J1", "J2", "J3"))
    count = int(math.ceil((maximum - minimum) / step_deg))
    pitches = [minimum + index * step_deg for index in range(count + 1)]
    pitches[-1] = maximum
    return pitches


def inverse_kinematics(
    x,
    y,
    z,
    *,
    current=DEFAULT_CURRENT,
    tool_pitch_deg=None,
    pitch_step_deg=0.25,
):
    """Return the nearest safe servo solution for a target XYZ position.

    Args:
        x, y, z: Gripper-center target in millimeters.
        current: Current J0-J5 servo angles, used to choose among valid results.
        tool_pitch_deg: Optional fixed tool pitch measured forward from vertical.
            If omitted, safe tool orientations are searched automatically.
        pitch_step_deg: Orientation search resolution when pitch is automatic.
    """
    if len(current) != 6:
        raise ValueError("current must contain six servo angles: J0 J1 J2 J3 J4 J5")
    current = tuple(float(value) for value in current)
    x, y, z = float(x), float(y), float(z)

    radius = math.hypot(x, y)
    if radius < 1e-9:
        q0_deg = current[0] - SERVO_CENTER_DEG
    else:
        q0_deg = math.degrees(math.atan2(-x, y))
    j0_servo = SERVO_CENTER_DEG + q0_deg
    if not _within_limit("J0", j0_servo):
        low, high = JOINT_LIMITS["J0"]
        raise InverseKinematicsError(
            f"target direction requires J0={j0_servo:.2f} deg; safe range is {low}..{high} deg"
        )

    shoulder_z = z - (B0 + H0)
    candidates = []
    for pitch_deg in _pitch_candidates(tool_pitch_deg, pitch_step_deg):
        pitch = math.radians(pitch_deg)
        wrist_radius = radius - TOOL_LENGTH * math.sin(pitch)
        wrist_z = shoulder_z - TOOL_LENGTH * math.cos(pitch)
        cosine_q2 = (
            wrist_radius**2 + wrist_z**2 - L1**2 - L2**2
        ) / (2.0 * L1 * L2)
        if cosine_q2 < -1.0 - 1e-9 or cosine_q2 > 1.0 + 1e-9:
            continue
        cosine_q2 = max(-1.0, min(1.0, cosine_q2))

        for elbow_sign, elbow_name in ((1.0, "positive"), (-1.0, "negative")):
            q2 = elbow_sign * math.acos(cosine_q2)
            q1 = math.atan2(wrist_radius, wrist_z) - math.atan2(
                L2 * math.sin(q2), L1 + L2 * math.cos(q2)
            )
            q3 = pitch - q1 - q2
            position_servos = (
                j0_servo,
                SERVO_CENTER_DEG + math.degrees(q1),
                SERVO_CENTER_DEG + math.degrees(q2),
                SERVO_CENTER_DEG + math.degrees(q3),
            )
            if not all(
                _within_limit(name, angle)
                for name, angle in zip(POSITION_JOINTS, position_servos)
            ):
                continue

            all_servos = position_servos + (current[4], current[5])
            predicted = robot_pose(*all_servos[:5])
            error = math.dist((x, y, z), predicted)
            score = _angle_distance_squared(position_servos, current)
            candidates.append((score, error, pitch_deg, elbow_name, all_servos))

    if not candidates:
        pitch_note = (
            " with the requested tool pitch"
            if tool_pitch_deg is not None
            else " within the configured joint limits"
        )
        raise InverseKinematicsError(
            f"no safe inverse-kinematics solution for x={x:g}, y={y:g}, z={z:g}{pitch_note}"
        )

    _, error, pitch_deg, elbow_name, servos = min(candidates, key=lambda item: (item[0], item[1]))
    return IKSolution(servos, pitch_deg, error, elbow_name)


def main():
    parser = argparse.ArgumentParser(
        description="Calculate safe J0-J3 servo angles from a gripper XYZ target."
    )
    parser.add_argument("x", type=float, help="left/right target in mm")
    parser.add_argument("y", type=float, help="forward target in mm")
    parser.add_argument("z", type=float, help="height target in mm")
    parser.add_argument(
        "--current",
        nargs=6,
        type=float,
        default=DEFAULT_CURRENT,
        metavar=("J0", "J1", "J2", "J3", "J4", "J5"),
        help="current servo angles; defaults to the 150-degree home pose",
    )
    parser.add_argument(
        "--tool-pitch",
        type=float,
        help="fix tool pitch in degrees forward from vertical (default: search automatically)",
    )
    parser.add_argument(
        "--pitch-step",
        type=float,
        default=0.25,
        help="automatic tool-pitch search resolution in degrees (default: 0.25)",
    )
    args = parser.parse_args()

    try:
        solution = inverse_kinematics(
            args.x,
            args.y,
            args.z,
            current=args.current,
            tool_pitch_deg=args.tool_pitch,
            pitch_step_deg=args.pitch_step,
        )
    except InverseKinematicsError as exc:
        parser.error(str(exc))

    angles = solution.servo_angles
    print(f"target: x={args.x:.1f} mm, y={args.y:.1f} mm, z={args.z:.1f} mm")
    print(f"tool pitch: {solution.tool_pitch_deg:.2f} deg ({solution.elbow} elbow solution)")
    print("servo angles J0 J1 J2 J3 J4 J5:")
    print(" ".join(f"{angle:.2f}" for angle in angles))
    print(f"forward-check error: {solution.position_error_mm:.6f} mm")
    print("\nCalculation only; no command was sent to the robot.")


if __name__ == "__main__":
    main()
