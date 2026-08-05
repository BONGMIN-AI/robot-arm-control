# Robot Arm Control

AX-12A 6-servo robot arm project. Jetson AGX Orin runs ROS2 Humble and directly controls the arm.

## Current Status

- Forward kinematics, actual AX-12A control, status readout, saved poses, and hand-taught recording/playback are working.
- `arm-record` recordings have been tested with several real motions.
- `robot_arm_description` now contains a basic xacro, launch file, and the available STL meshes.
- ROS2 workspace build and `source install/setup.bash` completed on Jetson.
- RViz visual output has not yet been verified. Do not mark URDF/RViz visualization as complete yet.

## Current Plan

1. Improve overheat, voltage, and communication-error logs.
2. Record safe motion boundaries with `arm-record` and derive joint-limit candidates.
3. Build the minimal STL + DH-based URDF/RViz model; verify joint direction visually in RViz.
4. Prepare Isaac Sim and ROS2 training environment in an NHN Cloud Docker GPU container.
5. Implement and test inverse kinematics.
6. Revisit Raspberry Pi HTTP motor-server separation only after the finished arm structure is stable.

Useful commands:

```powershell
# Forward kinematics
python kinematics\dh_calculator.py 150 180 180 150 150

# Safe interpolated motion plan
python kinematics\motion_plan.py --start 150 150 150 150 150 150 --target 150 180 180 150 150 150 --step 5
```

Coordinate convention:

- `x`: left/right from the base center
- `y`: forward from the base center
- `z`: height from the floor/table
- Servo center: `150 deg`
- Joint angle: `servo_angle - 150`
- `J5`: gripper open/close, excluded from arm position kinematics
