import argparse
import os
import sys
from pathlib import Path


REPO_ROOT = Path(os.environ.get("ROBOT_ARM_REPO", Path.cwd())).resolve()
sys.path.append(str(REPO_ROOT / "raspberry_pi"))

from read_status import load_driver, print_status, read_status


def main():
    parser = argparse.ArgumentParser(description="Print current AX-12A status for J0..J5.")
    parser.add_argument("--device", default="/dev/ttyUSB0")
    parser.add_argument("--baudrate", type=int, default=1_000_000)
    parser.add_argument("--mock", action="store_true")
    args = parser.parse_args()

    driver = load_driver(args.mock, args.device, args.baudrate)
    driver.connect()
    try:
        print_status(read_status(driver))
    finally:
        driver.close()


if __name__ == "__main__":
    main()
