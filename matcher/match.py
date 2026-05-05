import json

import faiss
import numpy as np

from matcher.config import FAISS_INDEX, FAISS_META, MISSIONS_OUT, RESULTS_OUT, TOP_K
from matcher.embeddings import embed_texts


async def run() -> None:
    if RESULTS_OUT.exists():
        print("Skipping matching")
        return

    with open(MISSIONS_OUT, encoding="utf-8") as f:
        missions_raw = json.load(f)
    with open(FAISS_META, encoding="utf-8") as f:
        candidates_raw = json.load(f)

    index = faiss.read_index(str(FAISS_INDEX))

    texts = [m["text_content"] for m in missions_raw]
    print(f"Embedding {len(texts)} missions and searching top {TOP_K}...")
    vectors = await embed_texts(texts)

    scores_matrix, indices_matrix = index.search(np.ascontiguousarray(vectors), TOP_K)  # type: ignore[arg-type]

    results = []
    for mission, scores, indices in zip(missions_raw, scores_matrix, indices_matrix):
        candidates = [
            {"candidate_id": candidates_raw[i]["id"], "score": round(float(s), 4)}
            for i, s in zip(indices, scores)
            if i != -1
        ]
        results.append({"mission_id": mission["id"], "candidates": candidates})

    with open(RESULTS_OUT, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"  -> {RESULTS_OUT}")
