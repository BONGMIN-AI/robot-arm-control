from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution
from launch_ros.parameter_descriptions import ParameterValue  # 추가


def generate_launch_description():
    pkg_share = FindPackageShare("robot_arm_description")
    xacro_file = PathJoinSubstitution([
        pkg_share,
        "urdf",
        "robot_arm.urdf.xacro",
    ])
    robot_description = {
        "robot_description": ParameterValue(
            Command([
                "xacro ",
                xacro_file,
            ]),
            value_type=str  # 이걸 명시 안 하면 launch_ros가 YAML로 파싱 시도함
        )
    }
    return LaunchDescription([
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            parameters=[robot_description],
        ),
        Node(
            package="joint_state_publisher_gui",
            executable="joint_state_publisher_gui",
        ),
        Node(
            package="rviz2",
            executable="rviz2",
            arguments=[],
            output="screen",
        ),
    ])
