import asyncio
import json
import os
from pathlib import Path

import faiss
import numpy as np
from openai import AsyncOpenAI

from .schema import Candidate

EMBED_MODEL = "text-embedding-3-small"
ROOT = Path(__file__).parent.parent
OUTPUTS = ROOT / "outputs"
CANDIDATES_OUT = OUTPUTS / "candidates.json"
FAISS_INDEX = OUTPUTS / "candidates.faiss"
FAISS_META = OUTPUTS / "candidates_meta.json"

client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

BATCH_SIZE = 100


async def _embed(texts: list[str]) -> np.ndarray:
    """Create embedding of the texts using openai embeddings"""
    batches = [texts[i : i + BATCH_SIZE] for i in range(0, len(texts), BATCH_SIZE)]
    responses = await asyncio.gather(
        *[client.embeddings.create(model=EMBED_MODEL, input=batch) for batch in batches]
    )
    all_embeddings = [
        e.embedding for r in responses for e in sorted(r.data, key=lambda x: x.index)
    ]
    vectors = np.array(all_embeddings, dtype=np.float32)
    faiss.normalize_L2(vectors)  # type: ignore[arg-type]
    return vectors


async def build() -> None:
    """Build the faiss vector index"""
    if FAISS_INDEX.exists() and FAISS_META.exists():
        print("Skipping embeddings")
        return

    with open(CANDIDATES_OUT, encoding="utf-8") as f:
        candidates_raw = json.load(f)

    texts = [c["text_content"] for c in candidates_raw]
    if not texts:
        raise ValueError("No candidates to embed")

    print(f"Embedding {len(texts)} candidates...")
    vectors = await _embed(texts)

    # normalize_L2 + IndexFlatIP = linear cosine similarity
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(np.ascontiguousarray(vectors))  # type: ignore[arg-type]
    faiss.write_index(index, str(FAISS_INDEX))

    with open(FAISS_META, "w", encoding="utf-8") as f:
        json.dump(candidates_raw, f, ensure_ascii=False, indent=2)

    print(f"  -> {FAISS_INDEX} ({len(texts)} vectors, dim={vectors.shape[1]})")


def search(query: str, k: int = 5) -> list[tuple[Candidate, float]]:
    index = faiss.read_index(str(FAISS_INDEX))
    with open(FAISS_META, encoding="utf-8") as f:
        candidates_raw = json.load(f)

    query_vec = asyncio.run(_embed([query]))
    scores, indices = index.search(query_vec, k)

    results = []
    for j, i in enumerate(indices[0]):
        if i == -1:
            continue
        results.append((Candidate(**candidates_raw[i]), float(scores[0][j])))
    return results
