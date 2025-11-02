from openai import OpenAI
import os
import json
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv("ai-slop.env")

OPENAI_API_KEY = os.getenv("OPEN_AI_KEY")

MIN_BLOCKS = 4                 # at least this many if content allows
TARGET_BLOCKS = 8              # try to hit this (ok to exceed)
MAX_BLOCK_SECONDS = 30.0       # per-block cap so long moments get split
MIN_BLOCK_SECONDS = 15.0        # avoid ultra-short clips when possible
MIN_SCORE = 7                  # 0–10 threshold for “interesting enough”

def refine_transcript(transcript: Dict, diarization) -> str:
    """Use OpenAI API to map speaker IDs to names and clean the transcript."""

    api_key = OPENAI_API_KEY 
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable not set")
    openai.api_key = api_key

    diarization_text = str(diarization)
    prompt = (
        "Given the following transcript and diarization output, replace speaker "
        "IDs with human friendly names and clean up the text.\n\nTranscript:\n"
        f"{json.dumps(transcript)}\n\nDiarization:\n{diarization_text}"
    )

    response = openai.responses.create(
        model="gpt-5-nano",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return response.choices[0].message.content


def analyze_impact(transcript_text: str, interesting_prompt: str) -> List[Dict[str, float]]:
    """Ask the OpenAI API for a list of impactful segments."""
    client = OpenAI(api_key = OPENAI_API_KEY)

    prompt_header = f"""
    You are given a list of transcript segments, each with start, end, and text.

    Goal: select MULTIPLE contiguous blocks of segments (e.g., [2,3,4] valid; [2,4] invalid)
    that represent the most interesting parts of the transcript. There is NO LIMIT on total
    duration across all blocks. If the video is great, return many blocks.

    Definition of interestingness: '{interesting_prompt}'

    RULES
    1) Each block MUST be sequential segments in input order (no gaps inside a block).
    2) Block duration = last_segment.end - first_segment.start.
       • ≤ {MAX_BLOCK_SECONDS} seconds per block. If a moment is longer, SPLIT it into adjacent blocks.
       • Aim for ≥ {MIN_BLOCK_SECONDS} seconds per block when possible.
    3) Return AT LEAST {MIN_BLOCKS} blocks if the content allows. Aim for ~{TARGET_BLOCKS} or more if warranted.
    4) Prefer multiple distinct high-interest moments over merging them into a single long block.
    5) Keep blocks non-overlapping and ordered by time. If two candidate blocks would overlap,
       keep the higher-interest one or split to avoid overlap.
    6) Use an internal 0–10 “interestingness score”. Only return blocks scoring ≥ {MIN_SCORE}.
    7) Titles should be short and catchy (zoomer vibe).

    OUTPUT
    Return JSON ONLY as an array of objects in this exact shape, no extra text:

    [
      {{
        "start_time": <float>,
        "end_time": <float>,
        "segment_ids": [<ints>],   // sequential
        "reason": "<why this section is most interesting>",
        "title": "<short zoomer-style title>"
      }}
      // repeat for as many blocks as you find
    ]

    Segments:
    """

    segments_json = json.dumps(transcript_text["segments"], indent=2)

    prompt = prompt_header + segments_json

    response = client.responses.create(
        model="gpt-5-mini",
        input=prompt,
    )
    data = json.loads(response.output_text)
    return data 
