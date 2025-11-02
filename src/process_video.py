import argparse
import json
import os
import subprocess

from typing import List, Dict
from download import download_youtube_video
from audio import extract_audio, transcribe_audio, diarize_audio

def run_pipeline(url: str, model_size: str = "base") -> None:
    print(f"Downloading youtube video")
    # video = download_youtube_video(url)
    video = "downloads/Nek Minute - Original.mp4"
    print(f"Finished Downloading Youtube Video")

    print("Extracting Audio")
    audio = extract_audio(video)
    print("Finish Extracting Audio")

    print("Transcribing Audio")
    transcript = transcribe_audio(audio, model_size)
    print("Finished Transcription")

    diarization = diarize_audio(audio)
    for segment, _, speaker in diarization.itertracks(yield_label=True):
        print(f"{segment.start:.1f}s - {segment.end:.1f}s: speaker {speaker}")

    # refined = refine_transcript(transcript, diarization)
    # segments = analyze_impact(refined)
    # clips = generate_clips(video, segments)

    with open("transcript.json", "w") as fh:
        json.dump(transcript, fh, indent=2)
        
    """
    with open("diarization.json", "w") as fh:
        json.dump(diarization, fh, indent=2)
    with open("refined_transcript.txt", "w") as fh:
        fh.write(refined)
    with open("segments.json", "w") as fh:
        json.dump(segments, fh, indent=2)

    print("Generated clips:")
    for clip in clips:
        print(f" - {clip}")
    """


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the end-to-end video processing pipeline"
    )
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument("--model-size", default="base", help="Whisper model size")

    args = parser.parse_args()
    run_pipeline(args.url, args.model_size)


if __name__ == "__main__":
    main()
