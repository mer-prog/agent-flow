"""Tests for core security utilities: password hashing, JWT tokens."""

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_hash_and_verify_password():
    hashed = hash_password("secure-pass-123")
    assert hashed != "secure-pass-123"
    assert verify_password("secure-pass-123", hashed)


def test_verify_wrong_password():
    hashed = hash_password("correct-password")
    assert not verify_password("wrong-password", hashed)


def test_access_token_roundtrip():
    data = {"sub": "user-123"}
    token = create_access_token(data)
    payload = decode_token(token)
    assert payload["sub"] == "user-123"
    assert payload["type"] == "access"


def test_refresh_token_roundtrip():
    data = {"sub": "user-456"}
    token = create_refresh_token(data)
    payload = decode_token(token)
    assert payload["sub"] == "user-456"
    assert payload["type"] == "refresh"


def test_access_token_is_not_refresh():
    token = create_access_token({"sub": "u1"})
    payload = decode_token(token)
    assert payload["type"] != "refresh"


def test_different_passwords_produce_different_hashes():
    h1 = hash_password("password1")
    h2 = hash_password("password2")
    assert h1 != h2
