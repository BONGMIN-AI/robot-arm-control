import sys
import os
from pathlib import Path

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray


REPO_ROOT = Path(os.environ.get("ROBOT_ARM_REPO", Path.cwd())).resolve()
sys.path.append(str(REPO_ROOT / "kinematics"))

from joint_config import JOINT_LIMITS


class JointCommandListener(Node):
    def __init__(self):
        super().__init__("joint_command_listener")
        self.subscription = self.create_subscription(
            Float64MultiArray,
            "robot_arm/joint_targets",
            self.on_joint_targets,
            10,
        )
        self.get_logger().info("Listening on /robot_arm/joint_targets")

    def on_joint_targets(self, msg):
        values = list(msg.data)
        if len(values) != 6:
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
