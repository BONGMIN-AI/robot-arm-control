class Ax12aDriver:
    """DYNAMIXEL AX-12A driver wrapper.

    Requires Robotis DynamixelSDK on Raspberry Pi:
        python3 -m pip install dynamixel-sdk
    """

    # AX-12A / Protocol 1.0 control table addresses.
    ADDR_TORQUE_ENABLE = 24
    ADDR_GOAL_POSITION = 30
    ADDR_MOVING_SPEED = 32
    ADDR_PRESENT_POSITION = 36
    ADDR_PRESENT_LOAD = 40
    ADDR_PRESENT_VOLTAGE = 42
    ADDR_PRESENT_TEMPERATURE = 43

    PROTOCOL_VERSION = 1.0
    DEFAULT_BAUDRATE = 1_000_000

    def __init__(self, device="/dev/ttyUSB0", baudrate=DEFAULT_BAUDRATE):
        self.device = device
        self.baudrate = baudrate
        self.port_handler = None
        self.packet_handler = None

    def connect(self):
        from dynamixel_sdk import PacketHandler, PortHandler

        self.port_handler = PortHandler(self.device)
        self.packet_handler = PacketHandler(self.PROTOCOL_VERSION)

        if not self.port_handler.openPort():
            raise RuntimeError(f"Failed to open DYNAMIXEL port: {self.device}")
        if not self.port_handler.setBaudRate(self.baudrate):
            raise RuntimeError(f"Failed to set baudrate: {self.baudrate}")

    def close(self):
        if self.port_handler:
            self.port_handler.closePort()

    def torque_on(self, servo_id):
        self._write1(servo_id, self.ADDR_TORQUE_ENABLE, 1)

    def torque_off(self, servo_id):
        self._write1(servo_id, self.ADDR_TORQUE_ENABLE, 0)

    def set_speed(self, servo_id, speed):
        self._write2(servo_id, self.ADDR_MOVING_SPEED, int(speed))

    def set_angle(self, servo_id, angle_deg):
        self._write2(servo_id, self.ADDR_GOAL_POSITION, angle_to_ax12_position(angle_deg))

    def get_angle(self, servo_id):
        raw = self._read2(servo_id, self.ADDR_PRESENT_POSITION)
        return ax12_position_to_angle(raw)

    def get_temperature_c(self, servo_id):
        return self._read1(servo_id, self.ADDR_PRESENT_TEMPERATURE)

    def get_voltage_v(self, servo_id):
        return self._read1(servo_id, self.ADDR_PRESENT_VOLTAGE) / 10.0

    def _write1(self, servo_id, address, value):
        result, error = self.packet_handler.write1ByteTxRx(
            self.port_handler, servo_id, address, int(value)
        )
        self._check(result, error, servo_id, address)

    def _write2(self, servo_id, address, value):
        result, error = self.packet_handler.write2ByteTxRx(
            self.port_handler, servo_id, address, int(value)
        )
        self._check(result, error, servo_id, address)

    def _read1(self, servo_id, address):
        value, result, error = self.packet_handler.read1ByteTxRx(
            self.port_handler, servo_id, address
        )
        self._check(result, error, servo_id, address)
        return value

    def _read2(self, servo_id, address):
        value, result, error = self.packet_handler.read2ByteTxRx(
            self.port_handler, servo_id, address
        )
        self._check(result, error, servo_id, address)
        return value

    def _check(self, result, error, servo_id, address):
        if result != 0:
            message = self.packet_handler.getTxRxResult(result)
            raise RuntimeError(f"Servo {servo_id} address {address}: {message}")
        if error != 0:
            message = self.packet_handler.getRxPacketError(error)
            raise RuntimeError(f"Servo {servo_id} address {address}: {message}")


def angle_to_ax12_position(angle_deg):
    angle = max(0.0, min(300.0, float(angle_deg)))
    return round(angle / 300.0 * 1023)


def ax12_position_to_angle(position):
    return float(position) / 1023.0 * 300.0

