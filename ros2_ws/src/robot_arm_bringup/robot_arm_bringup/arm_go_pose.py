import argparse
import os
import sys
from pathlib import Path


REPO_ROOT = Path(os.environ.get("ROBOT_ARM_REPO", Path.cwd())).resolve()
sys.path.append(str(REPO_ROOT / "kinematics"))
sys.path.append(str(REPO_ROOT / "raspberry_pi"))

from go_pose import go_pose
from pose_store import load_pose
from read_status import load_driver


def main():
    parser = argparse.ArgumentParser(description="Move to a saved robot arm pose.")
    parser.add_argument("name")
    parser.add_argument("--device", default="/dev/ttyUSB0")
    parser.add_argument("--baudrate", type=int, default=1_000_000)
    parser.add_argument("--step", type=float, default=1.0)
    parser.add_argument("--delay", type=float, default=0.08)
    parser.add_argument("--speed", type=int, default=50)
    parser.add_argument("--mock", action="store_true")
    parser.add_argument("--pose-dir", default=str(REPO_ROOT / "poses"))
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
