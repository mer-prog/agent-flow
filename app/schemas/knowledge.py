import uuid
from datetime import datetime

from pydantic import BaseModel


class KBArticleCreate(BaseModel):
    title: str
    content: str
    category: str | None = None


class KBArticleUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    category: str | None = None
    is_published: bool | None = None


class KBChunkResponse(BaseModel):
    id: uuid.UUID
    content: str
    chunk_index: int
    created_at: datetime

    model_config = {"from_attributes": True}


class KBArticleResponse(BaseModel):
    id: uuid.UUID
    title: str
    content: str
    category: str | None
    is_published: bool
    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}


class KBArticleDetail(KBArticleResponse):
    chunks: list[KBChunkResponse] = []


class KBArticleList(BaseModel):
    items: list[KBArticleResponse]
    total: int


class KBSearchRequest(BaseModel):
    query: str
    top_k: int = 5


class KBSearchResult(BaseModel):
    chunk_id: uuid.UUID
    article_id: uuid.UUID
    article_title: str
    content: str
    score: float
