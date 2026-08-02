import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "kinematics"))

from go_pose import go_pose
from motion_store import load_motion
from pose_store import load_pose
from read_status import JOINT_COUNT, load_driver
from torque_control import read_current_pose


def target_for_joints(current_pose, target_pose, joints):
    if joints is None:
        return list(target_pose)
    if not isinstance(joints, list) or not joints:
        raise ValueError("Step joints must be a non-empty list.")

    next_pose = list(current_pose)
    for joint in joints:
        if not isinstance(joint, int) or joint < 0 or joint >= JOINT_COUNT:
            raise ValueError("Step joints must contain servo ids from 0 to 5.")
        next_pose[joint] = target_pose[joint]
    return next_pose


def play_motion(
    driver,
    name,
    motion_dir,
    pose_dir,
    step_deg,
    delay_sec,
    speed,
    allow_unsafe,
    stack=None,
):
    stack = stack or []
    if name in stack:
        chain = " -> ".join(stack + [name])
        raise ValueError(f"Motion recursion detected: {chain}")

    path, data = load_motion(name, motion_dir)
    print(f"motion: {path}")

    for index, step in enumerate(data["steps"], start=1):
        if "motion" in step:
            print(f"step {index}: motion {step['motion']}")
            play_motion(
                driver,
                step["motion"],
                motion_dir,
                pose_dir,
                step.get("step", step_deg),
                step.get("delay", delay_sec),
                step.get("speed", speed),
                step.get("allow_unsafe", allow_unsafe),
                stack + [name],
            )
            continue

        if "pose" not in step:
            raise ValueError(f"Motion step {index} must contain pose or motion.")

        pose_path, pose_data = load_pose(step["pose"], pose_dir)
        current_pose = read_current_pose(driver)
        target_pose = target_for_joints(current_pose, pose_data["angles"], step.get("joints"))
        print(f"step {index}: pose {step['pose']} ({pose_path}) joints={step.get('joints', 'all')}")
        go_pose(
            driver,
            target_pose,
            step.get("step", step_deg),
            step.get("delay", delay_sec),
            step.get("speed", speed),
            step.get("allow_unsafe", allow_unsafe),
        )


def main():
    parser = argparse.ArgumentParser(description="Play a saved robot arm motion sequence.")
    parser.add_argument("name")
    parser.add_argument("--device", default="/dev/ttyUSB0")
    parser.add_argument("--baudrate", type=int, default=1_000_000)
    parser.add_argument("--step", type=float, default=1.0)
    parser.add_argument("--delay", type=float, default=0.08)
    parser.add_argument("--speed", type=int, default=50)
    parser.add_argument("--mock", action="store_true")
    parser.add_argument("--pose-dir", default=None)
    parser.add_argument("--motion-dir", default=None)
    parser.add_argument("--allow-unsafe", action="store_true")
    args = parser.parse_args()

    driver = load_driver(args.mock, args.device, args.baudrate)
    driver.connect()
    try:
        play_motion(
            driver,
            args.name,
            args.motion_dir,
            args.pose_dir,
            args.step,
            args.delay,
            args.speed,
            args.allow_unsafe,
        )
    finally:
        driver.close()


if __name__ == "__main__":
    main()
