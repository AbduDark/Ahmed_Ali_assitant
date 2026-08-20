"""Tests for authentication and security functions."""

from __future__ import annotations

import pytest
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_password_hashing():
    """Verify password hashing and verification."""
    raw_password = "SecurePassword123!"
    hashed = hash_password(raw_password)

    assert hashed != raw_password
    assert verify_password(raw_password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_access_token_creation_and_decoding():
    """Verify JWT access token generation and payload extraction."""
    user_id = "test-user-uuid-1234"
    role = "super_admin"

    token = create_access_token(user_id, role)
    assert isinstance(token, str)
    assert len(token) > 20

    payload = decode_token(token)
    assert payload["sub"] == user_id
    assert payload["role"] == role
    assert payload["type"] == "access"
    assert "exp" in payload


def test_refresh_token_creation():
    """Verify JWT refresh token generation."""
    user_id = "test-user-uuid-5678"
    token = create_refresh_token(user_id)

    payload = decode_token(token)
    assert payload["sub"] == user_id
    assert payload["type"] == "refresh"
    assert "exp" in payload
