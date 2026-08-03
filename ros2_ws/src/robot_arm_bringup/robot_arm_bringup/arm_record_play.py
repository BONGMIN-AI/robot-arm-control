import argparse
import os
import sys
from pathlib import Path


REPO_ROOT = Path(os.environ.get("ROBOT_ARM_REPO", Path.cwd())).resolve()
sys.path.append(str(REPO_ROOT / "raspberry_pi"))

from read_status import load_driver
from record_play import play_recording


def main():
    parser = argparse.ArgumentParser(description="Play a hand-recorded robot arm motion.")
    parser.add_argument("name")
    parser.add_argument("--device", default="/dev/ttyUSB0")
    parser.add_argument("--baudrate", type=int, default=1_000_000)
    parser.add_argument("--step", type=float, default=1.0)
    parser.add_argument("--delay", type=float, default=0.08)
    parser.add_argument("--speed", type=int, default=50)
    parser.add_argument("--grip-open", type=float, default=0.0)
    parser.add_argument("--grip-close", type=float, default=150.0)
    parser.add_argument("--grip-hold", type=float, default=1.0)
    parser.add_argument("--grip-tolerance", type=float, default=2.0)
    parser.add_argument("--grip-timeout", type=float, default=4.0)
    parser.add_argument("--mock", action="store_true")
    parser.add_argument("--recording-dir", default=str(REPO_ROOT / "recordings"))
    parser.add_argument("--allow-unsafe", action="store_true")
    args = parser.parse_args()

    driver = load_driver(args.mock, args.device, args.baudrate)
    driver.connect()
    try:
        play_recording(
            driver,
            args.name,
            args.recording_dir,
            args.step,
            args.delay,
            args.speed,
            args.grip_open,
            args.grip_close,
            args.grip_hold,
            args.grip_tolerance,
            args.grip_timeout,
            args.allow_unsafe,
        )
    finally:
        driver.close()


if __name__ == "__main__":
    main()
