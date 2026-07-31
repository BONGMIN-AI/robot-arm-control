import argparse
import math


# Measured robot dimensions in millimeters.
B0 = 85   # floor/table to J0 rotation center
H0 = 49   # J0 rotation center to J1 axis center
L1 = 109  # J1 axis center to J2 axis center
L2 = 109  # J2 axis center to J3 axis center
L3 = 63   # J3 axis center to J4 axis center
L4 = 104  # J4 axis center to gripper center/tool point


def servo_to_joint_angle(servo_deg):
    return servo_deg - 150


def robot_pose(j0_servo, j1_servo, j2_servo, j3_servo, j4_servo):
    """Forward kinematics for the vertical 150-degree home pose.

    Coordinate convention:
    x = side direction, y = front direction, z = up direction.
    J4 is gripper roll, so it changes tool orientation but not tool position.
    """
    q0 = math.radians(servo_to_joint_angle(j0_servo))
    q1 = math.radians(servo_to_joint_angle(j1_servo))
    q2 = math.radians(servo_to_joint_angle(j2_servo))
    q3 = math.radians(servo_to_joint_angle(j3_servo))

    c1 = q1
    c2 = q1 + q2
    c3 = q1 + q2 + q3

    wrist_and_tool = L3 + L4
    radius = (
        L1 * math.sin(c1)
        + L2 * math.sin(c2)
        + wrist_and_tool * math.sin(c3)
    )
    z = B0 + H0 + L1 * math.cos(c1) + L2 * math.cos(c2) + wrist_and_tool * math.cos(c3)

    x = -radius * math.sin(q0)
    y = radius * math.cos(q0)

    return x, y, z


def print_pose(name, pose):
    x, y, z = pose
    print(f"{name}: x={x:.1f} mm, y={y:.1f} mm, z={z:.1f} mm")


def main():
    parser = argparse.ArgumentParser(description="Calculate gripper position from J0-J4 servo angles.")
    parser.add_argument(
        "angles",
        nargs="*",
        type=float,
        help="Servo angles: J0 J1 J2 J3 J4. Example: 150 180 180 150 150",
    )
    args = parser.parse_args()

    print("Arm calculator for J0-J4. J5 gripper open/close is excluded.\n")
    print(f"Base height B0={B0} mm.")
    print("Servo center is 150 deg, so joint_angle = servo_angle - 150.\n")

    if args.angles:
        if len(args.angles) != 5:
            raise SystemExit("Please enter exactly five angles: J0 J1 J2 J3 J4")
        print_pose("custom", robot_pose(*args.angles))
        return

    tests = [
        ("home", (150, 150, 150, 150, 150)),
        ("J0 +30", (180, 150, 150, 150, 150)),
        ("J1 +30", (150, 180, 150, 150, 150)),
        ("J2 +30", (150, 150, 180, 150, 150)),
        ("J3 +30", (150, 150, 150, 180, 150)),
        ("J4 +30", (150, 150, 150, 150, 180)),
    ]

    for name, angles in tests:
        print_pose(name, robot_pose(*angles))


if __name__ == "__main__":
    main()

