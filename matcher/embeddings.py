import asyncio
import os

import faiss
import numpy as np
from openai import AsyncOpenAI

EMBED_MODEL = "text-embedding-3-small"
BATCH_SIZE = 100

client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


async def embed_texts(texts: list[str]) -> np.ndarray:
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
