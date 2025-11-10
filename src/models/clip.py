from typing import List
from pydantic import BaseModel, Field, validator


class Clip(BaseModel):
    start_time: float = Field(description="Start time (seconds) of the clip")
    end_time: float = Field(description="End time (seconds) of the clip")
    segment_ids: List[int] = Field(description="Sequential segment IDs in the block")
    reason: str = Field(description="Why this clip was selected (interest justification)")
    title: str = Field(description="Short, catchy title (zoomer vibe)")

    @validator("end_time")
    def validate_duration(cls, v, values):
        start = values.get("start_time")
        if start is not None and v <= start:
            raise ValueError("end_time must be greater than start_time")
        return v

    @validator("segment_ids")
    def validate_segment_sequence(cls, v):
        if not v:
            raise ValueError("segment_ids cannot be empty")
        # Ensure segments are sequential integers
        for i in range(1, len(v)):
            if v[i] != v[i - 1] + 1:
                raise ValueError("segment_ids must be sequential with no gaps")
        return v


class Clips(BaseModel):
    clips: List[Clip] = Field(description="List of all generated clip blocks")

    def to_json(self) -> str:
        """Return the list as a pure JSON array (for rule #OUTPUT)."""
        return self.json(
            indent=2,
            exclude_none=True,
            by_alias=True,
            encoder=lambda o: o.__dict__ if isinstance(o, BaseModel) else o,
        )
