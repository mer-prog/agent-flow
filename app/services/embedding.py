from __future__ import annotations

import hashlib
import struct

from app.config import settings

EMBEDDING_DIM = 1536
UINT32_MAX = 0xFFFFFFFF


def _sha256_pseudo_embedding(text: str) -> list[float]:
    """Generate a deterministic pseudo-embedding from SHA-256 hash.

    Used in demo mode when no OpenAI API key is available.
    """
    h = hashlib.sha256(text.lower().strip().encode()).digest()
    vectors: list[float] = []
    seed = h
    while len(vectors) < EMBEDDING_DIM:
        seed = hashlib.sha256(seed).digest()
        for i in range(0, 32, 4):
            val = struct.unpack("<I", seed[i : i + 4])[0]
            vectors.append((val / UINT32_MAX) * 2 - 1)
    return vectors[:EMBEDDING_DIM]


async def get_embedding(text: str) -> list[float]:
    """Get embedding for text. Uses OpenAI in live mode, SHA-256 in demo mode."""
    if settings.is_live_mode:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        resp = await client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
        )
        return resp.data[0].embedding

    return _sha256_pseudo_embedding(text)
