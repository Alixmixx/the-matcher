from typing import List
from datetime import date
from pydantic import BaseModel, Field, field_validator

class Candidate(BaseModel):
    """Extracted candidate profile"""
    id: str
    name: str
    available_from: date = Field(default_factory=date.today)

    @field_validator("available_from", mode="before")
    @classmethod
    def coerce_date(cls, v):
        if not v:
            return date.today()
        try:
            d = date.fromisoformat(str(v)) if isinstance(v, str) else v
            return d if d.year >= 2000 else date.today()
        except (ValueError, TypeError):
            return date.today()
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

class RankedCandidate(BaseModel):
    candidate_id: str
    score: float = Field(ge=0.0, le=1.0)
    justification: str
    evidence: List[str] = Field(default_factory=list)