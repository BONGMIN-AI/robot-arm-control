import argparse

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray


class JointTargetSender(Node):
    def __init__(self):
        super().__init__("joint_target_sender")
        self.publisher = self.create_publisher(Float64MultiArray, "robot_arm/joint_targets", 10)

    def send(self, angles):
        message = Float64MultiArray()
        message.data = [float(angle) for angle in angles]

        end_time = self.get_clock().now().nanoseconds + 500_000_000
        while self.get_clock().now().nanoseconds < end_time:
            rclpy.spin_once(self, timeout_sec=0.05)

        self.publisher.publish(message)
        self.get_logger().info(
            "Sent target: " + " ".join(f"J{i}={angle:.1f}" for i, angle in enumerate(message.data))
        )


def main():
    parser = argparse.ArgumentParser(description="Publish one robot arm joint target.")
    parser.add_argument("angles", nargs=6, type=float, metavar=("J0", "J1", "J2", "J3", "J4", "J5"))
    args = parser.parse_args()

    rclpy.init()
    node = JointTargetSender()
    try:
        node.send(args.angles)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()

