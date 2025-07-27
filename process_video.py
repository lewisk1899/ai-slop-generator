import argparse
import json
import os
import subprocess
from typing import List, Dict

from yt_dlp import YoutubeDL


def download_video(url: str, output_dir: str = "downloads") -> str:
    """Download a single YouTube video and return the path to the file."""
    os.makedirs(output_dir, exist_ok=True)
    ydl_opts = {
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s')
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_path = ydl.prepare_filename(info)
    return video_path


def extract_audio(video_path: str, output_dir: str = "audio") -> str:
    """Extract mono 16kHz WAV audio from the downloaded video."""
    os.makedirs(output_dir, exist_ok=True)
    base = os.path.splitext(os.path.basename(video_path))[0]
    audio_path = os.path.join(output_dir, f"{base}.wav")
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        video_path,
        "-ac",
        "1",
        "-ar",
        "16000",
        "-vn",
        audio_path,
    ]
    subprocess.run(cmd, check=True)
    return audio_path


def transcribe_audio(audio_path: str, model_size: str = "base") -> Dict:
    """Transcribe audio using Whisper."""
    import whisper

    model = whisper.load_model(model_size)
    result = model.transcribe(audio_path)
    return result


def diarize_audio(audio_path: str):
    """Run speaker diarization on the audio and return pyannote results."""
    from pyannote.audio import Pipeline

    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization")
    diarization = pipeline(audio_path)
    return diarization


def refine_transcript(transcript: Dict, diarization) -> str:
    """Use OpenAI API to map speaker IDs to names and clean the transcript."""
    import openai

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable not set")
    openai.api_key = api_key

    diarization_text = str(diarization)
    prompt = (
        "Given the following transcript and diarization output, replace speaker "
        "IDs with human friendly names and clean up the text.\n\nTranscript:\n"
        f"{json.dumps(transcript)}\n\nDiarization:\n{diarization_text}"
    )

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return response.choices[0].message.content


def analyze_impact(transcript_text: str) -> List[Dict[str, float]]:
    """Ask the OpenAI API for a list of impactful segments."""
    import openai

    openai.api_key = os.getenv("OPENAI_API_KEY")
    prompt = (
        "Identify the most impactful moments in the transcript and return a JSON "
        "array of objects with 'start' and 'end' fields in seconds."\
        f"\n\nTranscript:\n{transcript_text}"
    )
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    segments = json.loads(response.choices[0].message.content)
    return segments


def generate_clips(video_path: str, segments: List[Dict[str, float]], output_dir: str = "clips") -> List[str]:
    """Generate video clips based on the provided segments."""
    from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

    os.makedirs(output_dir, exist_ok=True)
    clip_paths = []
    for idx, segment in enumerate(segments):
        start = float(segment["start"])
        end = float(segment["end"])
        clip_path = os.path.join(output_dir, f"clip_{idx + 1}.mp4")
        ffmpeg_extract_subclip(video_path, start, end, targetname=clip_path)
        clip_paths.append(clip_path)
    return clip_paths


def run_pipeline(url: str, model_size: str = "base") -> None:
    video = download_video(url)
    audio = extract_audio(video)
    transcript = transcribe_audio(audio, model_size)
    diarization = diarize_audio(audio)
    refined = refine_transcript(transcript, diarization)
    segments = analyze_impact(refined)
    clips = generate_clips(video, segments)

    with open("transcript.json", "w") as fh:
        json.dump(transcript, fh, indent=2)
    with open("refined_transcript.txt", "w") as fh:
        fh.write(refined)
    with open("segments.json", "w") as fh:
        json.dump(segments, fh, indent=2)

    print("Generated clips:")
    for clip in clips:
        print(f" - {clip}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the end-to-end video processing pipeline")
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument("--model-size", default="base", help="Whisper model size")
    args = parser.parse_args()
    run_pipeline(args.url, args.model_size)


if __name__ == "__main__":
    main()
