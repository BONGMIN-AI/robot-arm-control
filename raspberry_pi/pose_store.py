import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from read_status import load_driver, read_status


POSE_NAME_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


def validate_pose_name(name):
    if not POSE_NAME_PATTERN.fullmatch(name):
        raise ValueError("Pose name may contain only letters, numbers, underscores, and hyphens.")


def default_pose_dir():
    return Path(__file__).resolve().parents[1] / "poses"


def pose_path(name, pose_dir=None):
    validate_pose_name(name)
    target_dir = Path(pose_dir) if pose_dir else default_pose_dir()
    return target_dir / f"{name}.json"


def list_poses(pose_dir=None):
    target_dir = Path(pose_dir) if pose_dir else default_pose_dir()
    if not target_dir.exists():
        return []
    return sorted(path.stem for path in target_dir.glob("*.json"))


def load_pose(name, pose_dir=None):
    path = pose_path(name, pose_dir)
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    angles = data.get("angles")
    if not isinstance(angles, list) or len(angles) != 6:
        raise ValueError(f"Pose {name} must contain six angles.")
    data["angles"] = [float(angle) for angle in angles]
    return path, data


def save_pose(name, rows, pose_dir=None):
    target_dir = Path(pose_dir) if pose_dir else default_pose_dir()
    target_dir.mkdir(parents=True, exist_ok=True)

    angles = [round(float(row["angle"]), 2) for row in rows]
    data = {
        "name": name,
        "angles": angles,
        "joints": [row["joint"] for row in rows],
        "source": "arm_status",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    path = pose_path(name, target_dir)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)
        file.write("\n")
    return path, data


def print_saved_pose(path, data):
    print(f"saved: {path}")
    print("angles:", " ".join(f"{angle:.2f}" for angle in data["angles"]))


def main():
    parser = argparse.ArgumentParser(description="Save the current robot arm pose to poses/<name>.json.")
    parser.add_argument("name")
    parser.add_argument("--device", default="/dev/ttyUSB0")
    parser.add_argument("--baudrate", type=int, default=1_000_000)
    parser.add_argument("--mock", action="store_true")
    parser.add_argument("--pose-dir", default=None)
    args = parser.parse_args()

    driver = load_driver(args.mock, args.device, args.baudrate)
    driver.connect()
    try:
        path, data = save_pose(args.name, read_status(driver), args.pose_dir)
        print_saved_pose(path, data)
    finally:
        driver.close()


if __name__ == "__main__":
    main()
