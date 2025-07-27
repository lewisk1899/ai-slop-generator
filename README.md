# ai-slop-generator

General Concept is take popular youtube videos, pass them through openai's whisper (https://github.com/openai/whisper) to diarize (convert them to subtitles with associated voice/speaker id's), then give the transcript to chat gpt/LLM's to map speaker ID's to real names, then take the transcript pass it to a LLM model for it to tell you the most impactful/interesting time sections for your user, and then programatically cut the video into those sections, do text overlay, and post it on instagram reels, tik tok, youtube shorts.

ai-slop-generator is effectively an automatic clip channel.

## Getting Started

Install dependencies:

```bash
pip install -r requirements.txt
```

### Downloading a Video

`download_video.py` is a small helper script that downloads a single YouTube video using [yt-dlp](https://pypi.org/project/yt-dlp/).

```bash
python download_video.py <video_url> [-o OUTPUT_DIRECTORY]
```

The downloaded file will be saved to the specified output directory (defaults to `downloads/`).

This script is the first step toward a future channel listener service that will
monitor channels and automatically download new uploads into a persistent volume.

### Full Pipeline Prototype

`process_video.py` demonstrates how the entire clipping pipeline could run in a
single script. It downloads a video, extracts audio, transcribes it with
[Whisper](https://github.com/openai/whisper), performs speaker diarization using
[pyannote.audio](https://github.com/pyannote/pyannote-audio), refines the
transcript with the OpenAI API, determines impactful segments, and finally
produces short clips with `moviepy`.

Running it requires `ffmpeg` on your `PATH` and valid credentials for the
OpenAI API via the `OPENAI_API_KEY` environment variable.

```bash
python process_video.py <video_url>
```

Generated clips and intermediate files will be stored in their respective
subdirectories under the current working directory.
