import pytest
from datetime import timedelta
from app.utils.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token
)


class TestPasswordHashing:
    """Test suite for password hashing utilities."""

    def test_password_hash_creates_different_hash(self):
        """Test that hashing the same password creates different hashes."""
        password = "testpassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert hash1 != hash2

    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "testpassword123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "testpassword123"
        hashed = get_password_hash(password)

        assert verify_password("wrongpassword", hashed) is False

    def test_long_password_hashing(self):
        """Test that passwords up to 72 bytes are handled correctly."""
        # Create a password of 70 bytes (within bcrypt's limit)
        long_password = "a" * 70
        hashed = get_password_hash(long_password)

        assert verify_password(long_password, hashed) is True

    def test_unicode_password_hashing(self):
        """Test that unicode passwords work correctly."""
        unicode_password = "パスワード🔐test密码"
        hashed = get_password_hash(unicode_password)

        assert verify_password(unicode_password, hashed) is True


class TestJWTTokens:
    """Test suite for JWT token utilities."""

    def test_create_access_token(self):
        """Test creating an access token."""
        data = {"sub": "user123", "email": "test@example.com"}
        token = create_access_token(data)

        assert token is not None
        assert isinstance(token, str)

    def test_decode_access_token(self):
        """Test decoding a valid access token."""
        data = {"sub": "user123", "email": "test@example.com"}
        token = create_access_token(data)

        decoded = decode_access_token(token)

        assert decoded is not None
        assert decoded["sub"] == "user123"
        assert decoded["email"] == "test@example.com"
        assert "exp" in decoded

    def test_decode_invalid_token(self):
        """Test decoding an invalid token."""
        invalid_token = "invalid.token.here"
        decoded = decode_access_token(invalid_token)

        assert decoded is None

    def test_create_token_with_custom_expiry(self):
        """Test creating token with custom expiration time."""
        data = {"sub": "user123"}
        expires_delta = timedelta(minutes=60)
        token = create_access_token(data, expires_delta)

        decoded = decode_access_token(token)

        assert decoded is not None
        assert decoded["sub"] == "user123"
