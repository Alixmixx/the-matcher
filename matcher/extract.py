import asyncio
import json
import os
import re

from openai import AsyncOpenAI

from matcher.config import (
    CANDIDATES_FILE, CANDIDATES_OUT,
    EXTRACT_MODEL, MISSIONS_FILE, MISSIONS_OUT, OUTPUTS,
)
from matcher.prompts import EXTRACT_CANDIDATE, EXTRACT_MISSION
from matcher.schema import Candidate, Mission

client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def _split_candidates(text: str) -> list[str]:
    blocks = re.split(r"\n={30}\n(?=CV #)", text)
    return [b.strip() for b in blocks if b.strip()]


async def extract_candidate(raw: str) -> Candidate:
    response = await client.responses.parse(
        model=EXTRACT_MODEL,
        input=[
            {
                "role": "system",
                "content": EXTRACT_CANDIDATE,
            },
            {"role": "user", "content": raw},
        ],
        text_format=Candidate,
        temperature=0,
    )
    if response.output_parsed is None:
        raise ValueError("Model did not return structured output for a candidate")
    candidate = response.output_parsed
    candidate.raw_content = raw
    return candidate


async def extract_mission(raw: dict) -> Mission:
    response = await client.responses.parse(
        model=EXTRACT_MODEL,
        input=[
            {
                "role": "system",
                "content": EXTRACT_MISSION,
            },
            {"role": "user", "content": json.dumps(raw, ensure_ascii=False, indent=2)},
        ],
        text_format=Mission,
        temperature=0,
    )
    if response.output_parsed is None:
        raise ValueError(
            f"Model did not return structured output for mission {raw['id']}"
        )
    mission = response.output_parsed
    mission.id = raw["id"]
    mission.raw_content = json.dumps(raw, ensure_ascii=False)
    return mission


async def run() -> None:
    OUTPUTS.mkdir(exist_ok=True)

    with open(CANDIDATES_FILE, encoding="utf-8") as f:
        candidats_text = f.read()
    with open(MISSIONS_FILE, encoding="utf-8") as f:
        missions_raw = json.load(f)["missions"]

    if CANDIDATES_OUT.exists():
        print("Skipping candidates")
    else:
        candidate_blocks = _split_candidates(candidats_text)
        print(f"Extracting {len(candidate_blocks)} candidates")
        candidates = await asyncio.gather(
            *[extract_candidate(block) for block in candidate_blocks]
        )
        with open(CANDIDATES_OUT, "w", encoding="utf-8") as f:
            json.dump(
                [c.model_dump(mode="json") for c in candidates],
                f,
                ensure_ascii=False,
                indent=2,
            )

    if MISSIONS_OUT.exists():
        print("Skipping missions")
    else:
        print(f"Extracting {len(missions_raw)} missions")
        missions = await asyncio.gather(*[extract_mission(m) for m in missions_raw])
        with open(MISSIONS_OUT, "w", encoding="utf-8") as f:
            json.dump(
                [m.model_dump(mode="json") for m in missions],
                f,
                ensure_ascii=False,
                indent=2,
            )

    print("Extraction finished")
