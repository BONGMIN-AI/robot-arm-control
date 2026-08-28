SERVO_CENTER_DEG = 150

# Configured servo limits shared by planners and motor-control commands.
# J5 is restricted to the gripper's verified 0..150 degree range.
JOINT_LIMITS = {
    "J0": (0, 300),
    "J1": (50, 250),
    "J2": (0, 300),
    "J3": (0, 300),
    "J4": (0, 300),
    "J5": (0, 150),
}


def clamp_angle(joint_name, angle):
    low, high = JOINT_LIMITS[joint_name]
    return max(low, min(high, angle))


def validate_angle(joint_name, angle):
    low, high = JOINT_LIMITS[joint_name]
    if not low <= angle <= high:
        raise ValueError(f"{joint_name} angle {angle} is outside safe range {low}..{high}")
