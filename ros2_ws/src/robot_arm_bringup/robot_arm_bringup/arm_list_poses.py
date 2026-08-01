import argparse
import os
import sys
from pathlib import Path


REPO_ROOT = Path(os.environ.get("ROBOT_ARM_REPO", Path.cwd())).resolve()
sys.path.append(str(REPO_ROOT / "raspberry_pi"))

from pose_store import list_poses


def main():
    parser = argparse.ArgumentParser(description="List saved robot arm poses.")
    parser.add_argument("--pose-dir", default=str(REPO_ROOT / "poses"))
    args = parser.parse_args()

    poses = list_poses(args.pose_dir)
    if not poses:
        print("No saved poses.")
        return

    for name in poses:
        print(name)


if __name__ == "__main__":
    main()
