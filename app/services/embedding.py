from __future__ import annotations

import hashlib
import struct

from app.config import settings


def _sha256_pseudo_embedding(text: str) -> list[float]:
    """Generate a deterministic 1536-d pseudo-embedding from SHA-256 hash.

    Used in demo mode when no OpenAI API key is available.
    """
    h = hashlib.sha256(text.lower().strip().encode()).digest()
    # Expand 32 bytes → 1536 floats by repeated hashing
    vectors: list[float] = []
    seed = h
    while len(vectors) < 1536:
        seed = hashlib.sha256(seed).digest()
        # Unpack 32 bytes as 8 floats (4 bytes each, little-endian unsigned int → normalise)
        for i in range(0, 32, 4):
            val = struct.unpack("<I", seed[i : i + 4])[0]
            vectors.append((val / 0xFFFFFFFF) * 2 - 1)  # normalise to [-1, 1]
    return vectors[:1536]


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
