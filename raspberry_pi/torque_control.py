import argparse
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "kinematics"))

from motion_plan import interpolate_motion
from read_status import JOINT_COUNT, load_driver


HOME_POSE = [150.0, 150.0, 150.0, 150.0, 150.0, 150.0]


def read_current_pose(driver):
    return [driver.get_angle(servo_id) for servo_id in range(JOINT_COUNT)]


def move_home(driver, step_deg, delay_sec, speed):
    start_pose = read_current_pose(driver)
    for servo_id in range(JOINT_COUNT):
        driver.torque_on(servo_id)
        driver.set_speed(servo_id, speed)

    path = interpolate_motion(start_pose, HOME_POSE, step_deg)
    for pose in path:
        print("home:", " ".join(f"{angle:.2f}" for angle in pose))
        for servo_id, angle in enumerate(pose):
            driver.set_angle(servo_id, angle)
        time.sleep(delay_sec)


def set_torque(driver, enabled):
    for servo_id in range(JOINT_COUNT):
        if enabled:
            driver.torque_on(servo_id)
        else:
            driver.torque_off(servo_id)


def main():
    parser = argparse.ArgumentParser(description="Turn AX-12A torque on or safely off.")
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
            time.sleep(1.0)
        set_torque(driver, False)
        print("torque: off")
    finally:
        driver.close()


if __name__ == "__main__":
    main()
