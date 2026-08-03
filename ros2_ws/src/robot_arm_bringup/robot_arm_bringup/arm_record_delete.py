import argparse
import os
import sys
from pathlib import Path


REPO_ROOT = Path(os.environ.get("ROBOT_ARM_REPO", Path.cwd())).resolve()
sys.path.append(str(REPO_ROOT / "raspberry_pi"))

from recording_store import delete_recording


def main():
    parser = argparse.ArgumentParser(description="Delete a saved hand-taught recording.")
    parser.add_argument("name")
    parser.add_argument("--recording-dir", default=str(REPO_ROOT / "recordings"))
    args = parser.parse_args()

    path = delete_recording(args.name, args.recording_dir)
    print(f"deleted: {path}")


if __name__ == "__main__":
    main()
