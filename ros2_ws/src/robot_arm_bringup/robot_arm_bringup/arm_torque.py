import argparse
import os
import sys
from pathlib import Path


REPO_ROOT = Path(os.environ.get("ROBOT_ARM_REPO", Path.cwd())).resolve()
sys.path.append(str(REPO_ROOT / "kinematics"))
sys.path.append(str(REPO_ROOT / "raspberry_pi"))

from torque_control import move_home, set_torque
from read_status import load_driver


def main():
    parser = argparse.ArgumentParser(description="Turn robot arm torque on or safely off.")
    parser.add_argument("state", choices=("on", "off"))
    parser.add_argument("--device", default="/dev/ttyUSB0")
    parser.add_argument("--baudrate", type=int, default=1_000_000)
    parser.add_argument("--step", type=float, default=1.0)
    parser.add_argument("--delay", type=float, default=0.08)
    parser.add_argument("--speed", type=int, default=50)
    parser.add_argument("--mock", action="store_true")
    parser.add_argument(
        "--no-home",
        action="store_true",
        help="Turn torque off without first moving to the home pose.",
    )
    args = parser.parse_args()

    driver = load_driver(args.mock, args.device, args.baudrate)
    driver.connect()
    try:
        if args.state == "on":
            set_torque(driver, True)
            print("torque: on")
            return

        if not args.no_home:
            move_home(driver, args.step, args.delay, args.speed)
        set_torque(driver, False)
        print("torque: off")
    finally:
        driver.close()


if __name__ == "__main__":
    main()
