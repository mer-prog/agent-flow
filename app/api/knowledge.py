from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, get_db
from app.models.knowledge import KBArticle
from app.models.user import User, UserRole
from app.schemas.knowledge import (
    KBArticleCreate,
    KBArticleDetail,
    KBArticleList,
    KBArticleResponse,
    KBArticleUpdate,
    KBSearchRequest,
    KBSearchResult,
)
from app.services.knowledge import chunk_and_embed_article, search_knowledge_base

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


@router.get("", response_model=KBArticleList)
async def list_articles(
    skip: int = 0,
    limit: int = 20,
    category: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> dict:
    query = select(KBArticle).where(KBArticle.is_published.is_(True))
    if category:
        query = query.where(KBArticle.category == category)

    total = await db.scalar(select(func.count()).select_from(query.subquery()))

    result = await db.execute(
        query.order_by(KBArticle.created_at.desc()).offset(skip).limit(limit)
    )
    items = list(result.scalars().all())

    return {"items": items, "total": total or 0}


@router.post("", response_model=KBArticleResponse, status_code=201)
async def create_article(
    body: KBArticleCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> KBArticle:
    if user.role == UserRole.customer:
        raise HTTPException(status_code=403, detail="Access denied")

    article = KBArticle(
        title=body.title,
        content=body.content,
        category=body.category,
    )
    db.add(article)
    await db.flush()

    # Chunk and embed
    await chunk_and_embed_article(db, article.id, body.content)

    await db.refresh(article)
    return article


@router.get("/{article_id}", response_model=KBArticleDetail)
async def get_article(
    article_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> KBArticle:
    result = await db.execute(
        select(KBArticle)
        .options(selectinload(KBArticle.chunks))
        .where(KBArticle.id == article_id)
    )
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.patch("/{article_id}", response_model=KBArticleResponse)
async def update_article(
    article_id: uuid.UUID,
    body: KBArticleUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> KBArticle:
    if user.role == UserRole.customer:
        raise HTTPException(status_code=403, detail="Access denied")

    result = await db.execute(select(KBArticle).where(KBArticle.id == article_id))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(article, field, value)

    # Re-chunk if content changed
    if "content" in update_data:
        # Delete old chunks
        for chunk in article.chunks:
            await db.delete(chunk)
        await db.flush()
        await chunk_and_embed_article(db, article.id, article.content)

    await db.refresh(article)
    return article


@router.delete("/{article_id}", status_code=204)
async def delete_article(
    article_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    if user.role == UserRole.customer:
        raise HTTPException(status_code=403, detail="Access denied")

    result = await db.execute(select(KBArticle).where(KBArticle.id == article_id))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    await db.delete(article)


@router.post("/search", response_model=list[KBSearchResult])
async def search(
    body: KBSearchRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    results = await search_knowledge_base(db, body.query, body.top_k)
    return results
