import argparse
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "kinematics"))

from go_pose import go_pose
from joint_config import validate_angle
from read_status import JOINT_COUNT, load_driver
from recording_store import load_recording
from torque_control import read_current_pose


HOME_POSE = [150.0, 150.0, 150.0, 150.0, 150.0, 150.0]
RECORD_JOINT_COUNT = 5
GRIP_MIN_DEG = 0.0
GRIP_MAX_DEG = 150.0


def full_pose(j0_to_j4, gripper_angle):
    return [float(angle) for angle in j0_to_j4] + [float(gripper_angle)]


def validate_recording_limits(data, grip_open, grip_close):
    for sample_index, sample in enumerate(data["samples"]):
        for joint_index, angle in enumerate(sample["joints"]):
            validate_angle(f"J{joint_index}", angle)


def validate_grip_settings(grip_open, grip_close, grip_hold, grip_tolerance, grip_timeout):
    for label, angle in (("--grip-open", grip_open), ("--grip-close", grip_close)):
        if not GRIP_MIN_DEG <= angle <= GRIP_MAX_DEG:
            raise ValueError(
                f"{label} angle {angle} is outside gripper range "
                f"{GRIP_MIN_DEG:.0f}..{GRIP_MAX_DEG:.0f}"
            )
    if grip_hold < 0:
        raise ValueError("--grip-hold must be greater than or equal to 0.")
    if grip_tolerance <= 0:
        raise ValueError("--grip-tolerance must be greater than 0.")
    if grip_timeout <= 0:
        raise ValueError("--grip-timeout must be greater than 0.")


def wait_for_grip(driver, target, tolerance, hold_sec, timeout_sec):
    deadline = time.monotonic() + timeout_sec
    while True:
        current = driver.get_angle(5)
        if abs(current - target) <= tolerance:
            time.sleep(hold_sec)
            return current
        if time.monotonic() >= deadline:
            raise TimeoutError(
                f"J5 did not reach {target:.2f} +/- {tolerance:.2f} deg "
                f"within {timeout_sec:.1f}s; current={current:.2f}"
            )
        time.sleep(0.05)


def send_pose(driver, pose, speed):
    for servo_id, angle in enumerate(pose):
        driver.set_speed(servo_id, speed)
        driver.set_angle(servo_id, angle)


def send_recorded_arm_pose(driver, j0_to_j4, speed):
    for servo_id, angle in enumerate(j0_to_j4):
        driver.set_speed(servo_id, speed)
        driver.set_angle(servo_id, angle)


def play_recording(
    driver,
    name,
    recording_dir,
    step_deg,
    delay_sec,
    speed,
    grip_open,
    grip_close,
    grip_hold,
    grip_tolerance,
    grip_timeout,
    allow_unsafe=False,
):
    path, data = load_recording(name, recording_dir)
    print(f"recording: {path}")
    validate_grip_settings(grip_open, grip_close, grip_hold, grip_tolerance, grip_timeout)
    if not allow_unsafe:
        validate_recording_limits(data, grip_open, grip_close)

    for servo_id in range(JOINT_COUNT):
        driver.torque_on(servo_id)
        driver.set_speed(servo_id, speed)

    print("move: home")
    go_pose(driver, HOME_POSE, step_deg, delay_sec, speed, allow_unsafe)

    first_sample = data["samples"][0]
    start_pose = full_pose(first_sample["joints"], grip_open)
    print("move: recording start")
    go_pose(driver, start_pose, step_deg, delay_sec, speed, allow_unsafe)

    events = sorted(data.get("events", []), key=lambda item: item["t"])
    next_event_index = 0
    playback_start = time.monotonic()
    previous_t = 0.0

    for sample in data["samples"]:
        sample_t = float(sample["t"])
        while next_event_index < len(events) and float(events[next_event_index]["t"]) <= sample_t:
            event = events[next_event_index]
            target = grip_open if event["type"] == "open" else grip_close
            print(f"event: {event['type']} target={target:.2f}")
            driver.set_speed(5, speed)
            hold_started = time.monotonic()
            driver.set_angle(5, target)
            reached = wait_for_grip(driver, target, grip_tolerance, grip_hold, grip_timeout)
            playback_start += time.monotonic() - hold_started
            print(f"event done: J5={reached:.2f}")
            next_event_index += 1

        target_time = playback_start + sample_t
        remaining = target_time - time.monotonic()
        if remaining > 0:
            time.sleep(remaining)

        send_recorded_arm_pose(driver, sample["joints"], speed)
        previous_t = sample_t

    while next_event_index < len(events):
        event = events[next_event_index]
        target = grip_open if event["type"] == "open" else grip_close
        print(f"event: {event['type']} target={target:.2f}")
        driver.set_speed(5, speed)
        driver.set_angle(5, target)
        reached = wait_for_grip(driver, target, grip_tolerance, grip_hold, grip_timeout)
        print(f"event done: J5={reached:.2f}")
        next_event_index += 1

    final_pose = read_current_pose(driver)
    print("final:", " ".join(f"{angle:.2f}" for angle in final_pose))


def main():
    parser = argparse.ArgumentParser(description="Play a hand-recorded J0..J4 motion.")
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
    parser.add_argument("--recording-dir", default=None)
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
