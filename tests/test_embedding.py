"""Tests for embedding service: demo mode SHA-256 pseudo-embedding."""

from app.services.embedding import _sha256_pseudo_embedding, EMBEDDING_DIM


def test_embedding_dimension():
    vec = _sha256_pseudo_embedding("test text")
    assert len(vec) == EMBEDDING_DIM


def test_embedding_deterministic():
    v1 = _sha256_pseudo_embedding("hello world")
    v2 = _sha256_pseudo_embedding("hello world")
    assert v1 == v2


def test_embedding_different_inputs():
    v1 = _sha256_pseudo_embedding("text a")
    v2 = _sha256_pseudo_embedding("text b")
    assert v1 != v2


def test_embedding_values_in_range():
    vec = _sha256_pseudo_embedding("range check")
    assert all(-1.0 <= v <= 1.0 for v in vec)


def test_embedding_case_insensitive():
    v1 = _sha256_pseudo_embedding("Hello")
    v2 = _sha256_pseudo_embedding("hello")
    assert v1 == v2


def test_embedding_strips_whitespace():
    v1 = _sha256_pseudo_embedding("  test  ")
    v2 = _sha256_pseudo_embedding("test")
    assert v1 == v2
