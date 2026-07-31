SERVO_CENTER_DEG = 150

# Conservative first-pass limits. Tighten or expand after mechanical testing.
JOINT_LIMITS = {
    "J0": (120, 180),
    "J1": (150, 185),
    "J2": (130, 200),
    "J3": (130, 200),
    "J4": (0, 300),
    "J5": (90, 210),
}


def clamp_angle(joint_name, angle):
    low, high = JOINT_LIMITS[joint_name]
    return max(low, min(high, angle))


def validate_angle(joint_name, angle):
    low, high = JOINT_LIMITS[joint_name]
    if not low <= angle <= high:
        raise ValueError(f"{joint_name} angle {angle} is outside safe range {low}..{high}")

