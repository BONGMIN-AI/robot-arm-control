import argparse
import os
import sys
from pathlib import Path


REPO_ROOT = Path(os.environ.get("ROBOT_ARM_REPO", Path.cwd())).resolve()
sys.path.append(str(REPO_ROOT / "raspberry_pi"))

from read_status import load_driver
from record_motion import record_motion


def main():
    parser = argparse.ArgumentParser(description="Record a hand-taught robot arm motion.")
    parser.add_argument("name")
    parser.add_argument("--device", default="/dev/ttyUSB0")
    parser.add_argument("--baudrate", type=int, default=1_000_000)
    parser.add_argument("--hz", type=float, default=20.0)
    parser.add_argument("--mock", action="store_true")
    parser.add_argument("--recording-dir", default=str(REPO_ROOT / "recordings"))
    args = parser.parse_args()

    driver = load_driver(args.mock, args.device, args.baudrate)
    driver.connect()
    try:
        record_motion(driver, args.name, args.recording_dir, args.hz)
    finally:
        driver.close()


if __name__ == "__main__":
    main()
