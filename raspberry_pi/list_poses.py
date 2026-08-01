import argparse

from pose_store import list_poses


def main():
    parser = argparse.ArgumentParser(description="List saved robot arm poses.")
    parser.add_argument("--pose-dir", default=None)
    args = parser.parse_args()

    poses = list_poses(args.pose_dir)
    if not poses:
        print("No saved poses.")
        return

    for name in poses:
        print(name)


if __name__ == "__main__":
    main()
