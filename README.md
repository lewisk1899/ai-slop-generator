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

This script is the first step toward a future channel listener service that will monitor channels and automatically download new uploads into a persistent volume.
