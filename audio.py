import subprocess
import os

from pyannote.audio import Pipeline
from typing import Dict
import torch
import whisper


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
        "48000",
        "-vn",
        audio_path,
    ]
    subprocess.run(cmd, check=True)
    return audio_path


def transcribe_audio(audio_path: str, model_size: str = "base") -> Dict:
    """Transcribe audio using Whisper."""
    device = "cuda" if torch.cuda.is_available() else "cpu"

    model = whisper.load_model(model_size, device=device)
    result = model.transcribe(audio_path)
    return result


def diarize_audio(audio_path: str):
    """Run speaker diarization on the audio and return pyannote results."""
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization")
    diarization = pipeline(audio_path)
    return diarization

