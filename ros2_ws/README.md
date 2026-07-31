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

Shorter sender:

```bash
ros2 run robot_arm_bringup send_joint_target 150 180 180 150 150 150
```

By default this runs in mock mode and prints servo commands without moving hardware.

## Run With AX-12A Hardware

Use only after dry-run testing:

```bash
ros2 run robot_arm_bringup joint_command_listener --ros-args \
  -p mock:=false \
  -p device:=/dev/ttyUSB0 \
  -p step_deg:=1.0 \
  -p delay_sec:=0.08 \
  -p speed:=50
```

Then publish a target:

```bash
ros2 topic pub --once /robot_arm/joint_targets std_msgs/msg/Float64MultiArray "{data: [150, 150, 160, 150, 150, 150]}"
```

Or:

```bash
ros2 run robot_arm_bringup send_joint_target 150 150 160 150 150 150
```

## Optional Bash Aliases

Add these to `~/.bashrc` on Jetson if desired:

```bash
alias arm-listen='cd ~/robot-arm-control/ros2_ws && source /opt/ros/humble/setup.bash && export ROBOT_ARM_REPO=~/robot-arm-control && source install/setup.bash && ros2 run robot_arm_bringup joint_command_listener'
alias arm-real='cd ~/robot-arm-control/ros2_ws && source /opt/ros/humble/setup.bash && export ROBOT_ARM_REPO=~/robot-arm-control && source install/setup.bash && ros2 run robot_arm_bringup joint_command_listener --ros-args -p mock:=false -p device:=/dev/ttyUSB1 -p step_deg:=1.0 -p delay_sec:=0.08 -p speed:=50'
alias arm-send='cd ~/robot-arm-control/ros2_ws && source /opt/ros/humble/setup.bash && source install/setup.bash && ros2 run robot_arm_bringup send_joint_target'
```

Usage:

```bash
arm-real
arm-send 150 150 160 150 150 150
```
