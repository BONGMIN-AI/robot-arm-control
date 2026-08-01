import json
import os
import tempfile
from pathlib import Path


DEFAULT_ANGLES = [150.0, 150.0, 150.0, 150.0, 150.0, 150.0]


class MockServoDriver:
    def __init__(self, state_path=None):
        default_path = Path(
            os.environ.get(
                "ROBOT_ARM_MOCK_STATE",
                str(Path(tempfile.gettempdir()) / "robot_arm_mock_state.json"),
            )
        )
        self.state_path = Path(state_path) if state_path else default_path
        self.angles = self._load_angles()

    def connect(self):
        print("mock: connect")

    def close(self):
        print("mock: close")

    def torque_on(self, servo_id):
        print(f"mock: torque_on id={servo_id}")

    def torque_off(self, servo_id):
        print(f"mock: torque_off id={servo_id}")

    def set_speed(self, servo_id, speed):
        print(f"mock: set_speed id={servo_id} speed={speed}")

    def set_angle(self, servo_id, angle_deg):
        self.angles[servo_id] = float(angle_deg)
        self._save_angles()
        print(f"mock: set_angle id={servo_id} angle={angle_deg:.2f}")

    def get_angle(self, servo_id):
        return self.angles[servo_id]

    def get_temperature_c(self, servo_id):
        return 25

    def get_voltage_v(self, servo_id):
        return 12.0

    def _load_angles(self):
        try:
            with self.state_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
            angles = data.get("angles", DEFAULT_ANGLES)
            if len(angles) != 6:
                return list(DEFAULT_ANGLES)
            return [float(angle) for angle in angles]
        except (OSError, ValueError, TypeError):
            return list(DEFAULT_ANGLES)

    def _save_angles(self):
        try:
            self.state_path.parent.mkdir(parents=True, exist_ok=True)
            with self.state_path.open("w", encoding="utf-8") as file:
                json.dump({"angles": self.angles}, file)
        except OSError as error:
            print(f"mock: failed to save state: {error}")
