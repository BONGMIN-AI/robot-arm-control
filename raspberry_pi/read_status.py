import argparse

from ax12a_driver import Ax12aDriver
from mock_driver import MockServoDriver


JOINT_COUNT = 6


def load_driver(mock, device, baudrate):
    if mock:
        return MockServoDriver()
    return Ax12aDriver(device=device, baudrate=baudrate)


def read_status(driver):
    rows = []
    for servo_id in range(JOINT_COUNT):
        rows.append(
            {
                "joint": f"J{servo_id}",
                "id": servo_id,
                "angle": driver.get_angle(servo_id),
                "voltage": driver.get_voltage_v(servo_id),
                "temperature": driver.get_temperature_c(servo_id),
            }
        )
    return rows


def print_status(rows):
    print("joint id angle_deg voltage_v temp_c")
    for row in rows:
        print(
            f"{row['joint']:>5} "
            f"{row['id']:>2} "
            f"{row['angle']:>9.2f} "
            f"{row['voltage']:>9.1f} "
            f"{row['temperature']:>6}"
        )


def main():
    parser = argparse.ArgumentParser(description="Read AX-12A position, voltage, and temperature.")
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
