import json
import re
from pathlib import Path


MOTION_NAME_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


def validate_motion_name(name):
    if not MOTION_NAME_PATTERN.fullmatch(name):
        raise ValueError("Motion name may contain only letters, numbers, underscores, and hyphens.")


def default_motion_dir():
    return Path(__file__).resolve().parents[1] / "motions"


def motion_path(name, motion_dir=None):
    validate_motion_name(name)
    target_dir = Path(motion_dir) if motion_dir else default_motion_dir()
    return target_dir / f"{name}.json"


def load_motion(name, motion_dir=None):
    path = motion_path(name, motion_dir)
    with path.open("r", encoding="utf-8-sig") as file:
        data = json.load(file)
    steps = data.get("steps")
    if not isinstance(steps, list) or not steps:
        raise ValueError(f"Motion {name} must contain at least one step.")
    data["name"] = data.get("name", name)
    return path, data


def list_motions(motion_dir=None):
    target_dir = Path(motion_dir) if motion_dir else default_motion_dir()
    if not target_dir.exists():
        return []
    return sorted(path.stem for path in target_dir.glob("*.json"))
