import argparse
import json

from typing import Protocol, Dict, List


# -----------------------------
# Dependency Interfaces (DI)
# -----------------------------

class VideoDownloader(Protocol):
    def download(self, url: str, dry_run: bool = False) -> str: ...


class AudioExtractor(Protocol):
    def extract(self, video_path: str) -> str: ...


class Transcriber(Protocol):
    def transcribe(self, audio_path: str, model_size: str) -> Dict: ...


class Analyzer(Protocol):
    def analyze(self, transcript: Dict, interesting_prompt: str) -> List[Dict]: ...


class ClipGenerator(Protocol):
    def generate(self, video_path: str, segments: List[Dict]) -> List[str]: ...


# -----------------------------
# Concrete Implementations
# (thin wrappers around your current modules)
# -----------------------------

from download import download_youtube_video
from audio import extract_audio, transcribe_audio
from llm_requests import analyze_impact
from clip_editor import generate_clips


class DefaultDownloader(VideoDownloader):
    def download(self, url: str, dry_run: bool = False) -> str:
        return download_youtube_video(url, dry_run=dry_run)


class DefaultAudioExtractor(AudioExtractor):
    def extract(self, video_path: str) -> str:
        return extract_audio(video_path)


class DefaultTranscriber(Transcriber):
    def transcribe(self, audio_path: str, model_size: str) -> Dict:
        return transcribe_audio(audio_path, model_size)


class DefaultAnalyzer(Analyzer):
    def analyze(self, transcript: Dict, interesting_prompt: str) -> List[Dict]:
        return analyze_impact(transcript, interesting_prompt)


class DefaultClipGenerator(ClipGenerator):
    def generate(self, video_path: str, segments: List[Dict]) -> List[str]:
        return generate_clips(video_path, segments)


# -----------------------------
# Pipeline Orchestrator (fully DI)
# -----------------------------

class VideoPipeline:
    def __init__(
        self,
        downloader: VideoDownloader,
        audio_extractor: AudioExtractor,
        transcriber: Transcriber,
        analyzer: Analyzer,
        clip_generator: ClipGenerator,
    ):
        self.downloader = downloader
        self.audio_extractor = audio_extractor
        self.transcriber = transcriber
        self.analyzer = analyzer
        self.clip_generator = clip_generator

    def run(self, url: str, model_size: str = "base", dry_run: bool = False):
        print("Downloading youtube video")
        video_path = self.downloader.download(url, dry_run)
        print("Finished Downloading Youtube Video")

        print("Extracting Audio")
        audio_path = self.audio_extractor.extract(video_path)
        print("Finished Extracting Audio")

        print("Transcribing Audio")
        transcript = self.transcriber.transcribe(audio_path, model_size)
        with open("transcript.json", "w") as fh:
            json.dump(transcript, fh, indent=2)
        print("Finished Transcription")

        interesting_prompt = (
            "humor, novelty, conflict resolution, surprising claims, strong emotions"
        )

        print("Analyzing transcript")
        segments = self.analyzer.analyze(transcript, interesting_prompt)
        print(f"The most interesting segments are: {segments}")

        print("Generating clips")
        clips = self.clip_generator.generate(video_path, segments)

        print("Generated clips:")
        for clip in clips:
            print(f" - {str(clip)}")

        return {
            "video": video_path,
            "audio": audio_path,
            "transcript": transcript,
            "segments": segments,
            "clips": clips,
        }


# -----------------------------
# CLI entrypoint
# -----------------------------

def run_pipeline_from_url(url: str, model_size: str = "base", dry_run: bool = False):
    pipeline = VideoPipeline(
        downloader=DefaultDownloader(),
        audio_extractor=DefaultAudioExtractor(),
        transcriber=DefaultTranscriber(),
        analyzer=DefaultAnalyzer(),
        clip_generator=DefaultClipGenerator(),
    )
    return pipeline.run(url, model_size, dry_run)


# KEEP this around if you still want CLI access
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the end-to-end video processing pipeline"
    )
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument("--model-size", default="base")
    parser.add_argument("--dry-run", default=False, action="store_true")
    args = parser.parse_args()

    run_pipeline_from_url(args.url, args.model_size, args.dry_run)
