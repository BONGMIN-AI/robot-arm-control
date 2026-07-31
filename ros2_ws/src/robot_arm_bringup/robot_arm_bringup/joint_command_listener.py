import sys
import os
import time
from pathlib import Path

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray


REPO_ROOT = Path(os.environ.get("ROBOT_ARM_REPO", Path.cwd())).resolve()
sys.path.append(str(REPO_ROOT / "kinematics"))
sys.path.append(str(REPO_ROOT / "raspberry_pi"))

from joint_config import JOINT_LIMITS
from motion_plan import interpolate_motion


JOINT_COUNT = 6


class JointCommandListener(Node):
    def __init__(self):
        super().__init__("joint_command_listener")
        self.declare_parameter("mock", True)
        self.declare_parameter("device", "/dev/ttyUSB0")
        self.declare_parameter("baudrate", 1_000_000)
        self.declare_parameter("step_deg", 2.0)
        self.declare_parameter("delay_sec", 0.05)
        self.declare_parameter("speed", 80)
        self.declare_parameter("start_pose", [150.0, 150.0, 150.0, 150.0, 150.0, 150.0])

        self.mock = self.get_parameter("mock").value
        self.device = self.get_parameter("device").value
        self.baudrate = self.get_parameter("baudrate").value
        self.step_deg = self.get_parameter("step_deg").value
        self.delay_sec = self.get_parameter("delay_sec").value
        self.speed = self.get_parameter("speed").value
        self.current_pose = list(self.get_parameter("start_pose").value)

        self.driver = self.load_driver()
        self.driver.connect()
        for servo_id in range(JOINT_COUNT):
            self.driver.torque_on(servo_id)
            self.driver.set_speed(servo_id, self.speed)

        self.subscription = self.create_subscription(
            Float64MultiArray,
            "robot_arm/joint_targets",
            self.on_joint_targets,
            10,
        )
        mode = "mock" if self.mock else f"device={self.device}"
        self.get_logger().info(f"Listening on /robot_arm/joint_targets ({mode})")

    def destroy_node(self):
        if hasattr(self, "driver") and self.driver:
            self.driver.close()
        super().destroy_node()

    def load_driver(self):
        if self.mock:
            from mock_driver import MockServoDriver

            return MockServoDriver()

        from ax12a_driver import Ax12aDriver

        return Ax12aDriver(device=self.device, baudrate=self.baudrate)

    def on_joint_targets(self, msg):
        values = list(msg.data)
        if len(values) != JOINT_COUNT:
            self.get_logger().error(f"Expected 6 joint angles, got {len(values)}")
            return

        for index, angle in enumerate(values):
            joint_name = f"J{index}"
            low, high = JOINT_LIMITS[joint_name]
            if not low <= angle <= high:
                self.get_logger().error(
                    f"{joint_name} angle {angle:.1f} outside safe range {low}..{high}"
                )
                return

        self.get_logger().info(
            "Accepted target: " + " ".join(f"J{i}={angle:.1f}" for i, angle in enumerate(values))
        )
        path = interpolate_motion(self.current_pose, values, self.step_deg)
        self.get_logger().info(f"Generated {len(path)} motion steps")

        for pose in path:
            for servo_id, angle in enumerate(pose):
                self.driver.set_angle(servo_id, angle)
            self.current_pose = pose
            time.sleep(self.delay_sec)


def main():
    rclpy.init()
    node = JointCommandListener()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
