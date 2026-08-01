import argparse

from joint_config import JOINT_LIMITS, clamp_angle


JOINT_NAMES = ("J0", "J1", "J2", "J3", "J4", "J5")


def interpolate_motion(start, target, step_deg=2.0, clamp=True):
    if len(start) != 6 or len(target) != 6:
        raise ValueError("start and target must contain six servo angles: J0 J1 J2 J3 J4 J5")

    if clamp:
        target_pose = [
            clamp_angle(joint_name, angle)
            for joint_name, angle in zip(JOINT_NAMES, target)
        ]
    else:
        target_pose = [float(angle) for angle in target]

    max_delta = max(abs(t - s) for s, t in zip(start, target_pose))
    steps = max(1, int(max_delta / step_deg + 0.999))

    path = []
    for i in range(steps + 1):
        ratio = i / steps
        pose = [
            round(s + (t - s) * ratio, 2)
            for s, t in zip(start, target_pose)
        ]
        path.append(pose)
    return path


def main():
    parser = argparse.ArgumentParser(description="Generate safe interpolated servo steps.")
    parser.add_argument("--start", nargs=6, type=float, required=True, metavar=JOINT_NAMES)
    parser.add_argument("--target", nargs=6, type=float, required=True, metavar=JOINT_NAMES)
    parser.add_argument("--step", type=float, default=2.0, help="Maximum degrees per step")
    args = parser.parse_args()

    path = interpolate_motion(args.start, args.target, args.step)
    print("Joint limits:")
    for joint_name in JOINT_NAMES:
        print(f"  {joint_name}: {JOINT_LIMITS[joint_name][0]}..{JOINT_LIMITS[joint_name][1]}")
    print()
    print(f"Generated {len(path)} poses:")
    for pose in path:
        print(" ".join(f"{angle:.2f}" for angle in pose))


if __name__ == "__main__":
    main()
