# Robot Arm Control

6-servo robot arm project.

Current plan:

1. Calibrate forward kinematics.
2. Add inverse kinematics.
3. Add Raspberry Pi servo control.
4. Install ROS2 on Jetson AGX.
5. Connect Jetson, Raspberry Pi, and the robot arm through ROS2.

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
