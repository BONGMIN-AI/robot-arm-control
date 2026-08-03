import argparse
import os
import select
import sys
import termios
import time
import tty

from read_status import JOINT_COUNT, load_driver
from recording_store import save_recording
from torque_control import move_home, set_torque


RECORD_JOINT_COUNT = 5


class RawKeyboard:
    def __enter__(self):
        self.fd = sys.stdin.fileno()
        self.old_settings = termios.tcgetattr(self.fd)
        tty.setcbreak(self.fd)
        return self

    def __exit__(self, exc_type, exc, tb):
        termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_settings)

    def read_key(self):
        ready, _, _ = select.select([sys.stdin], [], [], 0)
        if not ready:
            return None
        return sys.stdin.read(1)


def read_record_pose(driver):
    return [float(driver.get_angle(servo_id)) for servo_id in range(RECORD_JOINT_COUNT)]


def prepare_for_hand_recording(driver, step_deg, delay_sec, speed):
    print("[DON'T TOUCH while torque off]")
    move_home(driver, step_deg, delay_sec, speed)
    set_torque(driver, False)
    print("torque: off")


def record_motion(driver, name, recording_dir, hz, step_deg, delay_sec, speed):
    prepare_for_hand_recording(driver, step_deg, delay_sec, speed)

    period = 1.0 / hz
    samples = []
    events = []

    print("Set the start pose by hand, then press SPACE to start recording.")
    print("During recording: o=open event, c=close event, q=stop.")

    with RawKeyboard() as keyboard:
        while True:
            key = keyboard.read_key()
            if key == " ":
                break
            time.sleep(0.02)

        start_time = time.monotonic()
        next_sample_at = start_time
        print("recording started")

        while True:
            now = time.monotonic()
            elapsed = now - start_time

            key = keyboard.read_key()
            if key == "q":
                break
            if key == "o":
                events.append({"t": round(elapsed, 3), "type": "open"})
                print(f"event open t={elapsed:.3f}")
            elif key == "c":
                events.append({"t": round(elapsed, 3), "type": "close"})
                print(f"event close t={elapsed:.3f}")

            if now >= next_sample_at:
                samples.append(
                    {
                        "t": round(elapsed, 3),
                        "joints": [round(angle, 2) for angle in read_record_pose(driver)],
                    }
                )
                next_sample_at += period

            time.sleep(0.005)

    path = save_recording(name, samples, events, recording_dir)
    print(f"saved: {path}")
    print(f"samples={len(samples)} events={len(events)}")
    return path


def main():
    parser = argparse.ArgumentParser(description="Record a hand-taught J0..J4 motion.")
    parser.add_argument("name")
    parser.add_argument("--device", default="/dev/ttyUSB0")
    parser.add_argument("--baudrate", type=int, default=1_000_000)
    parser.add_argument("--hz", type=float, default=20.0)
    parser.add_argument("--step", type=float, default=1.0)
    parser.add_argument("--delay", type=float, default=0.08)
    parser.add_argument("--speed", type=int, default=50)
    parser.add_argument("--mock", action="store_true")
    parser.add_argument("--recording-dir", default=None)
    args = parser.parse_args()

    if args.hz <= 0:
        raise ValueError("--hz must be greater than 0.")
    if os.name != "posix":
        raise RuntimeError("arm-record currently requires a POSIX terminal on Jetson/Linux.")

    driver = load_driver(args.mock, args.device, args.baudrate)
    driver.connect()
    try:
        record_motion(
            driver,
            args.name,
            args.recording_dir,
            args.hz,
            args.step,
            args.delay,
            args.speed,
        )
    finally:
        driver.close()


if __name__ == "__main__":
    main()
