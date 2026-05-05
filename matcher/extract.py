import asyncio
import json
import os
import re
from pathlib import Path

from openai import AsyncOpenAI

from matcher.schema import Candidate, Mission

# MODEL = "gpt-5.4-mini"
MODEL = "gpt-5.4-nano"
ROOT = Path(__file__).parent.parent
OUTPUTS = ROOT / "outputs"
DATA = ROOT / "data"
CANDIDATES_FILE = DATA / "candidats.txt"
MISSIONS_FILE = DATA / "missions.json"
CANDIDATES_OUT = OUTPUTS / "candidates.json"
MISSIONS_OUT = OUTPUTS / "missions.json"

client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def _split_candidates(text: str) -> list[str]:
    blocks = re.split(r"\n={30}\n(?=CV #)", text)
    return [b.strip() for b in blocks if b.strip()]


async def extract_candidate(raw: str) -> Candidate:
    response = await client.responses.parse(
        model=MODEL,
        input=[
            {
                "role": "system",
                "content": (
                    "Extract a structured candidate profile from the resume. "
                    "The candidate ID is in the header line 'CV #NNN — Name'. "
                    "Format it as C001, C002, etc. "
                    "For available_from: use the earliest date the candidate is available. "
                    "If immediately available or the date is unknown, set it to null. "
                    "For text_content, produce a clean normalized French version "
                    "suitable for semantic embedding."
                ),
            },
            {"role": "user", "content": raw},
        ],
        text_format=Candidate,
    )
    if response.output_parsed is None:
        raise ValueError("Model did not return structured output for a candidate")
    candidate = response.output_parsed
    candidate.raw_content = raw
    return candidate


async def extract_mission(raw: dict) -> Mission:
    """Structured extarction of missions"""
    response = await client.responses.parse(
        model=MODEL,
        input=[
            {
                "role": "system",
                "content": (
                    "Extract a structured mission from the JSON record. "
                    "For text_content, write a single fluent French paragraph "
                    "summarising the role, requirements, location and urgency "
                    "optimised for semantic similarity search."
                ),
            },
            {"role": "user", "content": json.dumps(raw, ensure_ascii=False, indent=2)},
        ],
        text_format=Mission,
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
        print(f"Skipping candidates")
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
        print(f"Skipping missions")
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
