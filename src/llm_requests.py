from openai import OpenAI
import os
import json
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv("ai-slop.env")

OPENAI_API_KEY=os.getenv("OPEN_AI_KEY")

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
    prompt = (
        "Read the transcript and return the single most interesting time section in a json JSON "
        "array of objects with 'start' and 'end' fields in seconds."
        f"\n\nTranscript:\n{transcript_text}"
    )
    response = client.responses.create(
        model="gpt-5-nano",
        input=prompt,
    )
    data = json.loads(response.output_text)
    #segments = json.loads(response.choices[0].message.content)
    return data 
