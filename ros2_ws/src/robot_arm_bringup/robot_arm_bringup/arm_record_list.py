import argparse
import os
import sys
from pathlib import Path


REPO_ROOT = Path(os.environ.get("ROBOT_ARM_REPO", Path.cwd())).resolve()
sys.path.append(str(REPO_ROOT / "raspberry_pi"))

from recording_store import list_recordings


def main():
    parser = argparse.ArgumentParser(description="List saved hand-taught recordings.")
    parser.add_argument("--recording-dir", default=str(REPO_ROOT / "recordings"))
    args = parser.parse_args()

    recordings = list_recordings(args.recording_dir)
    if not recordings:
        print("No saved recordings.")
        return

    for name in recordings:
        print(name)


if __name__ == "__main__":
    main()
