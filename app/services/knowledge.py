from __future__ import annotations

import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import cast, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.knowledge import KBArticle, KBChunk
from app.services.embedding import get_embedding


async def search_knowledge_base(
    db: AsyncSession,
    query: str,
    top_k: int = 5,
) -> list[dict]:
    """Search the knowledge base using vector similarity."""
    query_embedding = await get_embedding(query)

    # Cosine distance search using pgvector
    stmt = (
        select(
            KBChunk.id,
            KBChunk.article_id,
            KBChunk.content,
            KBArticle.title.label("article_title"),
            (
                1
                - KBChunk.embedding.cosine_distance(cast(query_embedding, Vector(1536)))
            ).label("score"),
        )
        .join(KBArticle, KBChunk.article_id == KBArticle.id)
        .where(KBArticle.is_published.is_(True))
        .where(KBChunk.embedding.isnot(None))
        .order_by(text("score DESC"))
        .limit(top_k)
    )

    result = await db.execute(stmt)
    rows = result.all()

    return [
        {
            "chunk_id": str(row.id),
            "article_id": str(row.article_id),
            "article_title": row.article_title,
            "content": row.content,
            "score": float(row.score) if row.score is not None else 0.0,
        }
        for row in rows
    ]


async def chunk_and_embed_article(
    db: AsyncSession,
    article_id: uuid.UUID,
    content: str,
    chunk_size: int = 500,
) -> list[KBChunk]:
    """Split article content into chunks and generate embeddings."""
    # Simple sentence-aware chunking
    sentences = content.replace("\n", " ").split(". ")
    chunks: list[str] = []
    current = ""

    for sentence in sentences:
        if len(current) + len(sentence) > chunk_size and current:
            chunks.append(current.strip())
            current = sentence + ". "
        else:
            current += sentence + ". "
    if current.strip():
        chunks.append(current.strip())

    kb_chunks = []
    for i, chunk_text in enumerate(chunks):
        embedding = await get_embedding(chunk_text)
        chunk = KBChunk(
            article_id=article_id,
            content=chunk_text,
            embedding=embedding,
            chunk_index=i,
        )
        db.add(chunk)
        kb_chunks.append(chunk)

    await db.flush()
    return kb_chunks
