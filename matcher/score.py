import asyncio
import json
import os

from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from matcher.config import (
    CANDIDATES_OUT, FINAL_OUT, MISSIONS_OUT, RESULTS_OUT, SCORE_MODEL, TOP_N,
)
from matcher.prompts import SCORE_CANDIDATE
from matcher.schema import Candidate, Mission

client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


class LLMScore(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    justification: str
    evidence: list[str]
    hard_excluded: bool = False
    exclusion_reason: str = ""


async def score_candidate(mission: Mission, candidate: Candidate) -> LLMScore:
    prompt = f"""Mission :
- Titre : {mission.title}
- Secteur : {mission.sector}
- Lieu : {mission.location}
- Début : {mission.start_date}  |  Durée : {mission.duration_months} mois  |  Urgence : {mission.urgency}
- Description : {mission.description}

Candidat {candidate.id} — {candidate.name} :
- Disponible immédiatement : {candidate.available_immediately}
- Disponible dès : {candidate.available_from if not candidate.available_immediately else "maintenant"}
- Localisation : {candidate.location}
- Certifications : {", ".join(candidate.certs) if candidate.certs else "aucune"}
- Note agence : {candidate.note}

Profil complet :
{candidate.raw_content}"""

    response = await client.responses.parse(
        model=SCORE_MODEL,
        input=[
            {
                "role": "system",
                "content": SCORE_CANDIDATE,
            },
            {"role": "user", "content": prompt},
        ],
        text_format=LLMScore,
        temperature=0,
    )
    if response.output_parsed is None:
        raise ValueError(f"No LLM output for candidate {candidate.id} on mission {mission.id}")
    return response.output_parsed


async def score_mission(
    mission: Mission, candidates: list[Candidate]
) -> tuple[list[dict], list[dict]]:
    scored = await asyncio.gather(
        *[score_candidate(mission, c) for c in candidates]
    )

    ranked = []
    filtered_out = []
    for candidate, llm_score in zip(candidates, scored):
        if llm_score.hard_excluded:
            filtered_out.append({"candidate_id": candidate.id, "reason": llm_score.exclusion_reason})
        else:
            ranked.append({
                "candidate_id": candidate.id,
                "score": round(llm_score.score, 4),
                "justification": llm_score.justification,
                "evidence": llm_score.evidence,
            })

    ranked.sort(key=lambda x: x["score"], reverse=True)
    return ranked[:TOP_N], filtered_out


async def run() -> None:
    if FINAL_OUT.exists():
        print("Skipping scoring")
        return

    with open(RESULTS_OUT, encoding="utf-8") as f:
        results_raw = json.load(f)
    with open(CANDIDATES_OUT, encoding="utf-8") as f:
        candidates_raw = json.load(f)
    with open(MISSIONS_OUT, encoding="utf-8") as f:
        missions_raw = json.load(f)

    candidates_by_id = {c["id"]: Candidate(**c) for c in candidates_raw}
    missions_by_id = {m["id"]: Mission(**m) for m in missions_raw}

    final = []
    for result in results_raw:
        mission_id = result["mission_id"]
        mission = missions_by_id[mission_id]
        candidates = [
            candidates_by_id[c["candidate_id"]]
            for c in result["candidates"]
            if c["candidate_id"] in candidates_by_id
        ]

        print(f"Scoring {mission_id} ({mission.title}): {len(candidates)} candidates...")
        ranked, filtered_out = await score_mission(mission, candidates)

        final.append({
            "mission_id": mission_id,
            "ranked_candidates": ranked,
            "filtered_out": filtered_out,
        })

    with open(FINAL_OUT, "w", encoding="utf-8") as f:
        json.dump(final, f, ensure_ascii=False, indent=2)

    print(f"  -> {FINAL_OUT}")
