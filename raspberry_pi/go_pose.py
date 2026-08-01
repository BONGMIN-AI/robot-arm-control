import argparse
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "kinematics"))

from motion_plan import interpolate_motion
from pose_store import load_pose
from read_status import JOINT_COUNT, load_driver
from torque_control import read_current_pose


def go_pose(driver, target_angles, step_deg, delay_sec, speed):
    start_pose = read_current_pose(driver)
    for servo_id in range(JOINT_COUNT):
        driver.torque_on(servo_id)
        driver.set_speed(servo_id, speed)

    path = interpolate_motion(start_pose, target_angles, step_deg)
    for pose in path:
        print("move:", " ".join(f"{angle:.2f}" for angle in pose))
        for servo_id, angle in enumerate(pose):
            driver.set_angle(servo_id, angle)
        time.sleep(delay_sec)


def main():
    parser = argparse.ArgumentParser(description="Move to a saved robot arm pose.")
    parser.add_argument("name")
    parser.add_argument("--device", default="/dev/ttyUSB0")
    parser.add_argument("--baudrate", type=int, default=1_000_000)
    parser.add_argument("--step", type=float, default=1.0)
    parser.add_argument("--delay", type=float, default=0.08)
    parser.add_argument("--speed", type=int, default=50)
    parser.add_argument("--mock", action="store_true")
    parser.add_argument("--pose-dir", default=None)
    args = parser.parse_args()

    path, data = load_pose(args.name, args.pose_dir)
    print(f"loaded: {path}")

    driver = load_driver(args.mock, args.device, args.baudrate)
    driver.connect()
    try:
        go_pose(driver, data["angles"], args.step, args.delay, args.speed)
    finally:
        driver.close()


if __name__ == "__main__":
    main()
