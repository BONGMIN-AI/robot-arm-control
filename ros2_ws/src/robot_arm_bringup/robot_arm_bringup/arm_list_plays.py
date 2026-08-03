import argparse
import os
import sys
from pathlib import Path


REPO_ROOT = Path(os.environ.get("ROBOT_ARM_REPO", Path.cwd())).resolve()
sys.path.append(str(REPO_ROOT / "raspberry_pi"))

from motion_store import list_motions


def main():
    parser = argparse.ArgumentParser(description="List saved arm-play motion sequences.")
    parser.add_argument("--motion-dir", default=str(REPO_ROOT / "motions"))
    args = parser.parse_args()

    motions = list_motions(args.motion_dir)
    if not motions:
        print("No saved plays.")
        return

    for name in motions:
        print(name)


if __name__ == "__main__":
    main()
