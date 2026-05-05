import asyncio
import json
from pathlib import Path

import faiss
import numpy as np

from matcher.embeddings import embed_texts
from matcher.schema import Candidate

ROOT = Path(__file__).parent.parent
OUTPUTS = ROOT / "outputs"
CANDIDATES_OUT = OUTPUTS / "candidates.json"
FAISS_INDEX = OUTPUTS / "candidates.faiss"
FAISS_META = OUTPUTS / "candidates_meta.json"


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
    vectors = await embed_texts(texts)

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

    query_vec = asyncio.run(embed_texts([query]))
    scores, indices = index.search(query_vec, k)

    results = []
    for j, i in enumerate(indices[0]):
        if i == -1:
            continue
        results.append((Candidate(**candidates_raw[i]), float(scores[0][j])))
    return results
