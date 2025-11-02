from openai import OpenAI
import os
import json
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv("ai-slop.env")

OPENAI_API_KEY = os.getenv("OPEN_AI_KEY")
NUM_SECONDS_MAX = 30

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


def analyze_impact(transcript_text: str) -> List[Dict[str, float]]:
    """Ask the OpenAI API for a list of impactful segments."""
    client = OpenAI(api_key = OPENAI_API_KEY)
    prompt = f"""
    You are given a list of transcript segments, each with start, end, and text.

    Your goal: select one contiguous block of segments (for example: [2,3,4] but not [2,4])
    that forms the most interesting or engaging part of the transcript.

    Rules:
    1. The selected segments must be sequential in the input order.
    2. The total time window (last_segment.end - first_segment.start) must be ≤ {NUM_SECONDS_MAX} seconds.
    3. Choose the block that maximizes overall "interestingness" within that limit.
    4. Output JSON only in this format:
    {{
      "start_time": <float>,
      "end_time": <float>,
      "segment_ids": [<ints>],
      "reason": "<why this section is most interesting>",
      "title": "<a good title for this clip>"
    }}

    Segments:
    {json.dumps(transcript_text["segments"], indent=2)}
    """

    response = client.responses.create(
        model="gpt-5-nano",
        input=prompt,
    )
    data = json.loads(response.output_text)
    return data 
