import argparse
import ast
from trimmer import trim


def main():
    trimer = argparse.ArgumentParser(description="Trims a given video into clip(s)")

    trimer.add_argument("file_path", help="File path to video")
    trimer.add_argument(
        "time_stamps",
        help="A list of tuples where each tuple is the start and end time of a clip to be made",
    )
    trimer.add_argument(
        "-o",
        "--output_dir",
        default="clips",
        help="The directory for the clips to be saved to",
    )

    args = trimer.parse_args()

    try:
        times = ast.literal_eval(args.time_stamps)
        if not isinstance(times, list) or not all(isinstance(t, tuple) for t in times):
            raise ValueError
    except Exception:
        print(
            "Error: time_stamps must be a valid list of tuples, e.g. [(0,10),(20,30)]"
        )
        return

    result = trim(args.file_path, args.output_dir, times)

    if result:
        print("Clips made!")
    else:
        print("something went wrong")


if __name__ == "__main__":
    main()
