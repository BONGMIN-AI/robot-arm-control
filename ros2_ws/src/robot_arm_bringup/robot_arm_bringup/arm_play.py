import argparse
import os
import sys
from pathlib import Path


REPO_ROOT = Path(os.environ.get("ROBOT_ARM_REPO", Path.cwd())).resolve()
sys.path.append(str(REPO_ROOT / "raspberry_pi"))

from play_motion import play_motion
from read_status import load_driver


def main():
    parser = argparse.ArgumentParser(description="Play a saved robot arm motion sequence.")
    parser.add_argument("name")
    parser.add_argument("--device", default="/dev/ttyUSB0")
    parser.add_argument("--baudrate", type=int, default=1_000_000)
    parser.add_argument("--step", type=float, default=1.0)
    parser.add_argument("--delay", type=float, default=0.08)
    parser.add_argument("--speed", type=int, default=50)
    parser.add_argument("--mock", action="store_true")
    parser.add_argument("--pose-dir", default=str(REPO_ROOT / "poses"))
    parser.add_argument("--motion-dir", default=str(REPO_ROOT / "motions"))
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
