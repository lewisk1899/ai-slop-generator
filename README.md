# ai-slop-generator
General Concept is take popular youtube videos, pass them through openai's whisper (https://github.com/openai/whisper) to diarize (convert them to subtitles with associated voice/speaker id's), then give the transcript to chat gpt/LLM's to map speaker ID's to real names, then take the transcript pass it to a LLM model for it to tell you the most impactful/interesting time sections for your user, and then programatically cut the video into those sections, do text overlay, and post it on instagram reels, tik tok, youtube shorts.

ai-slop-generator is effectively an automatic clip channel
