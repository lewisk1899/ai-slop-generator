import argparse
import os
import ast
import ffmpeg


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


def trim(video_clip: str, out: str, times: list) -> bool:
    """
    Trims a video into one or more clips depending on the amount of time ranges passed in.

    Parameters
    ----------

    video_clip : str
        the file path for the video clip
    out : str
        the file output path for the clip(s)
    times : list
        list of time ranges to create clips from

    Returns
    -------
    bool
        if the clip(s) were made sucessfully
    """
    if os.path.exists(video_clip) == False:
        print(f"Video: {video_clip} no found")
        return False

    os.makedirs(out, exist_ok=True)

    probe_result = ffmpeg.probe(video_clip)
    duration = probe_result.get("format", {}).get("duration", None)
    print(duration)

    input_stream = ffmpeg.input(video_clip)

    pts = "PTS-STARTPTS"

    base_name = os.path.splitext(os.path.basename(video_clip))[0]

    for idx, (start, end) in enumerate(times, start=1):
        video = input_stream.trim(start=start, end=end).setpts(pts)
        audio = input_stream.filter("atrim", start=start, end=end).filter(
            "asetpts", pts
        )
        video_and_audio = ffmpeg.concat(video, audio, v=1, a=1)

        output_path = os.path.join(out, f"{base_name}_clip_{idx}.mp4")
        ffmpeg.output(video_and_audio, output_path, format="mp4").run(
            overwrite_output=True
        )

    return True


if __name__ == "__main__":
    main()
