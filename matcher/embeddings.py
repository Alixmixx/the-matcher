import asyncio
import os

import faiss
import numpy as np
from openai import AsyncOpenAI

from matcher.config import EMBED_BATCH_SIZE, EMBED_MODEL

client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


async def embed_texts(texts: list[str]) -> np.ndarray:
    batches = [texts[i : i + EMBED_BATCH_SIZE] for i in range(0, len(texts), EMBED_BATCH_SIZE)]
    responses = await asyncio.gather(
        *[client.embeddings.create(model=EMBED_MODEL, input=batch) for batch in batches]
    )
    all_embeddings = [
        e.embedding for r in responses for e in sorted(r.data, key=lambda x: x.index)
    ]
    vectors = np.array(all_embeddings, dtype=np.float32)
    faiss.normalize_L2(vectors)  # type: ignore[arg-type]
    return vectors
