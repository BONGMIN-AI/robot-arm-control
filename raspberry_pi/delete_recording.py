import argparse

from recording_store import delete_recording


def main():
    parser = argparse.ArgumentParser(description="Delete a saved hand-taught recording.")
    parser.add_argument("name")
    parser.add_argument("--recording-dir", default=None)
    args = parser.parse_args()

    path = delete_recording(args.name, args.recording_dir)
    print(f"deleted: {path}")


if __name__ == "__main__":
    main()
