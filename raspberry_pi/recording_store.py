import json
import re
from pathlib import Path


RECORDING_NAME_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")
EVENT_TYPES = {"open", "close"}


def validate_recording_name(name):
    if not RECORDING_NAME_PATTERN.fullmatch(name):
        raise ValueError(
            "Recording name may contain only letters, numbers, underscores, and hyphens."
        )


def default_recording_dir():
    return Path(__file__).resolve().parents[1] / "recordings"


def recording_path(name, recording_dir=None):
    validate_recording_name(name)
    target_dir = Path(recording_dir) if recording_dir else default_recording_dir()
    return target_dir / f"{name}.json"


def save_recording(name, samples, events, recording_dir=None):
    if not samples:
        raise ValueError("Recording must contain at least one sample.")

    path = recording_path(name, recording_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "name": name,
        "version": 1,
        "joint_ids": [0, 1, 2, 3, 4],
        "samples": samples,
        "events": events,
    }
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)
        file.write("\n")
    return path


def load_recording(name, recording_dir=None):
    path = recording_path(name, recording_dir)
    with path.open("r", encoding="utf-8-sig") as file:
        data = json.load(file)
    validate_recording_data(data, name)
    data["name"] = data.get("name", name)
    return path, data


def list_recordings(recording_dir=None):
    target_dir = Path(recording_dir) if recording_dir else default_recording_dir()
    if not target_dir.exists():
        return []
    return sorted(path.stem for path in target_dir.glob("*.json"))


def validate_recording_data(data, expected_name=None):
    samples = data.get("samples")
    if not isinstance(samples, list) or not samples:
        raise ValueError("Recording must contain at least one sample.")

    previous_t = -1.0
    for index, sample in enumerate(samples):
        if not isinstance(sample, dict):
            raise ValueError(f"Sample {index} must be an object.")
        t = sample.get("t")
        joints = sample.get("joints")
        if not isinstance(t, (int, float)) or t < 0:
            raise ValueError(f"Sample {index} has invalid time.")
        if t < previous_t:
            raise ValueError(f"Sample {index} time goes backwards.")
        if not isinstance(joints, list) or len(joints) != 5:
            raise ValueError(f"Sample {index} must contain J0..J4 angles.")
        for joint_index, angle in enumerate(joints):
            if not isinstance(angle, (int, float)):
                raise ValueError(f"Sample {index} J{joint_index} angle is invalid.")
        previous_t = float(t)

    for index, event in enumerate(data.get("events", [])):
        if not isinstance(event, dict):
            raise ValueError(f"Event {index} must be an object.")
        if event.get("type") not in EVENT_TYPES:
            raise ValueError(f"Event {index} type must be open or close.")
        t = event.get("t")
        if not isinstance(t, (int, float)) or t < 0:
            raise ValueError(f"Event {index} has invalid time.")

    if expected_name is not None and data.get("name", expected_name) != expected_name:
        raise ValueError("Recording name does not match file name.")
