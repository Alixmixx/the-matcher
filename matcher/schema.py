from typing import List
from datetime import date
from pydantic import BaseModel, Field, field_validator

class Candidate(BaseModel):
    """Extracted candidate profile"""
    id: str
    name: str
    available_immediately: bool = False
    available_from: date | None = None

    @field_validator("available_from", mode="before")
    @classmethod
    def coerce_date(cls, v):
        if not v:
            return None
        try:
            d = date.fromisoformat(str(v)) if isinstance(v, str) else v
            return d if d.year >= 2000 else None
        except (ValueError, TypeError):
            return None
    text_content: str = Field(description="Normalized French version of the resume for embedding")
    raw_content: str = Field(description="Original resume text")
    note: str = Field(description="Agency note")
    location: str = Field(description="City")
    certs: List[str] = Field(description="List of candidate certifications")


class Mission(BaseModel):
    id: str
    title: str
    start_date: date
    duration_months: int
    urgency: str
    description: str
    sector: str
    location: str = Field(description="City")
    raw_content: str = Field(description="Original mission text")
    text_content: str = Field(description="Normalized French version of the resume for embedding")
    required_certs: list[str] = Field(
        default_factory=list,
        description="Legally mandatory certifications for this mission, empty if none",
    )

class RankedCandidate(BaseModel):
    candidate_id: str
    score: float = Field(ge=0.0, le=1.0)
    justification: str
    evidence: List[str] = Field(default_factory=list)