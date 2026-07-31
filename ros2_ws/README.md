# ROS2 Workspace

Placeholder for future ROS2 packages.

Planned packages:

- robot description
- kinematics utilities
- Raspberry Pi bridge
- Jetson high-level controller

## Build On Jetson

```bash
cd ~/robot-arm-control/ros2_ws
source /opt/ros/humble/setup.bash
export ROBOT_ARM_REPO=~/robot-arm-control
colcon build
source install/setup.bash
```

## Test Listener

Terminal 1:

```bash
ros2 run robot_arm_bringup joint_command_listener
```

Terminal 2:

```bash
ros2 topic pub --once /robot_arm/joint_targets std_msgs/msg/Float64MultiArray "{data: [150, 180, 180, 150, 150, 150]}"
```
