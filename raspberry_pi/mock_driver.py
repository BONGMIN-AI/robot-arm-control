class MockServoDriver:
    def __init__(self):
        self.angles = [150.0, 150.0, 150.0, 150.0, 150.0, 150.0]

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
        print(f"mock: set_angle id={servo_id} angle={angle_deg:.2f}")

    def get_angle(self, servo_id):
        return self.angles[servo_id]

    def get_temperature_c(self, servo_id):
        return 25

    def get_voltage_v(self, servo_id):
        return 12.0
