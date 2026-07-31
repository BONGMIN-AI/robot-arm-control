import argparse
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "kinematics"))

from joint_config import JOINT_LIMITS
from motion_plan import JOINT_NAMES, interpolate_motion


def load_driver(mock, device, baudrate):
    if mock:
        from mock_driver import MockServoDriver

        return MockServoDriver()

    from ax12a_driver import Ax12aDriver

    return Ax12aDriver(device=device, baudrate=baudrate)


def main():
    parser = argparse.ArgumentParser(description="Move AX-12A servos through a safe interpolated path.")
    parser.add_argument("target", nargs=6, type=float, metavar=JOINT_NAMES)
    parser.add_argument("--start", nargs=6, type=float, default=[150, 150, 150, 150, 150, 150])
    parser.add_argument("--step", type=float, default=2.0)
    parser.add_argument("--delay", type=float, default=0.05)
    parser.add_argument("--speed", type=int, default=80)
    parser.add_argument("--device", default="/dev/ttyUSB0")
    parser.add_argument("--baudrate", type=int, default=1_000_000)
    parser.add_argument("--mock", action="store_true")
    args = parser.parse_args()

    print("Joint limits:")
    for joint_name in JOINT_NAMES:
        print(f"  {joint_name}: {JOINT_LIMITS[joint_name][0]}..{JOINT_LIMITS[joint_name][1]}")
    print()

    path = interpolate_motion(args.start, args.target, args.step)
    driver = load_driver(args.mock, args.device, args.baudrate)
    driver.connect()

    try:
        for servo_id in range(6):
            driver.torque_on(servo_id)
            driver.set_speed(servo_id, args.speed)

        for pose in path:
            print("move:", " ".join(f"{angle:.2f}" for angle in pose))
            for servo_id, angle in enumerate(pose):
                driver.set_angle(servo_id, angle)
            time.sleep(args.delay)
    finally:
        driver.close()


if __name__ == "__main__":
    main()

