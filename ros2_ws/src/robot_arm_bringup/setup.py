from setuptools import setup


package_name = "robot_arm_bringup"

setup(
    name=package_name,
    version="0.0.1",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="BOMIN",
    maintainer_email="todo@example.com",
    description="ROS2 bringup nodes for the AX-12A robot arm.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "arm_play = robot_arm_bringup.arm_play:main",
            "arm_record = robot_arm_bringup.arm_record:main",
            "arm_record_list = robot_arm_bringup.arm_record_list:main",
            "arm_record_play = robot_arm_bringup.arm_record_play:main",
            "arm_go_pose = robot_arm_bringup.arm_go_pose:main",
            "arm_list_poses = robot_arm_bringup.arm_list_poses:main",
            "arm_save_pose = robot_arm_bringup.arm_save_pose:main",
            "arm_status = robot_arm_bringup.arm_status:main",
            "arm_torque = robot_arm_bringup.arm_torque:main",
            "joint_command_listener = robot_arm_bringup.joint_command_listener:main",
            "send_joint_target = robot_arm_bringup.send_joint_target:main",
        ],
    },
)
