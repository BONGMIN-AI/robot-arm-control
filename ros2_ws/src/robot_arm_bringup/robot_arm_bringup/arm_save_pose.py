import argparse
import os
import sys
from pathlib import Path


REPO_ROOT = Path(os.environ.get("ROBOT_ARM_REPO", Path.cwd())).resolve()
sys.path.append(str(REPO_ROOT / "raspberry_pi"))

from pose_store import print_saved_pose, save_pose
from read_status import load_driver, read_status


def main():
    parser = argparse.ArgumentParser(description="Save the current robot arm pose.")
    parser.add_argument("name")
    parser.add_argument("--device", default="/dev/ttyUSB0")
    parser.add_argument("--baudrate", type=int, default=1_000_000)
    parser.add_argument("--mock", action="store_true")
    parser.add_argument("--pose-dir", default=str(REPO_ROOT / "poses"))
    args = parser.parse_args()

    driver = load_driver(args.mock, args.device, args.baudrate)
    driver.connect()
    try:
        path, data = save_pose(args.name, read_status(driver), args.pose_dir)
        print_saved_pose(path, data)
    finally:
        driver.close()


if __name__ == "__main__":
    main()
