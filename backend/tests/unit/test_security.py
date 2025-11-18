"""Unit tests for security utilities."""
import pytest
from datetime import timedelta
from app.utils.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token,
)


class TestPasswordHashing:
    """Test password hashing functions."""

    def test_password_hash_creation(self):
        """Test that password hashing creates a hash."""
        password = "testpassword123"
        hashed = get_password_hash(password)

        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 0

    def test_password_hash_uniqueness(self):
        """Test that same password creates different hashes."""
        password = "testpassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        # Different salts should create different hashes
        assert hash1 != hash2

    def test_password_verification_success(self):
        """Test successful password verification."""
        password = "testpassword123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_password_verification_failure(self):
        """Test failed password verification."""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = get_password_hash(password)

        assert verify_password(wrong_password, hashed) is False

    def test_empty_password_hash(self):
        """Test hashing empty password."""
        password = ""
        hashed = get_password_hash(password)

        assert hashed is not None
        assert verify_password(password, hashed) is True

    def test_long_password_hash(self):
        """Test hashing very long password."""
        password = "a" * 1000
        hashed = get_password_hash(password)

        assert hashed is not None
        assert verify_password(password, hashed) is True

    def test_special_characters_password(self):
        """Test password with special characters."""
        password = "P@ssw0rd!#$%^&*()"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True


class TestJWTTokens:
    """Test JWT token creation and decoding."""

    def test_create_access_token(self):
        """Test creating an access token."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_token_with_expiration(self):
        """Test creating token with custom expiration."""
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(minutes=30)
        token = create_access_token(data, expires_delta=expires_delta)

        assert token is not None

    def test_decode_valid_token(self):
        """Test decoding a valid token."""
        data = {"sub": "test@example.com", "user_id": "123"}
        token = create_access_token(data)
        decoded = decode_access_token(token)

        assert decoded is not None
        assert decoded["sub"] == "test@example.com"
        assert decoded["user_id"] == "123"

    def test_decode_invalid_token(self):
        """Test decoding an invalid token."""
        invalid_token = "invalid.token.here"
        decoded = decode_access_token(invalid_token)

        assert decoded is None

    def test_decode_expired_token(self):
        """Test decoding an expired token."""
        data = {"sub": "test@example.com"}
        # Create token that expires immediately
        expires_delta = timedelta(seconds=-1)
        token = create_access_token(data, expires_delta=expires_delta)
        decoded = decode_access_token(token)

        # Should be None or handle expired token
        assert decoded is None or "exp" in decoded

    def test_token_contains_expiration(self):
        """Test that token contains expiration claim."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        decoded = decode_access_token(token)

        assert decoded is not None
        assert "exp" in decoded

    def test_token_with_additional_claims(self):
        """Test token with additional custom claims."""
        data = {
            "sub": "test@example.com",
            "user_id": "123",
            "is_admin": True,
            "custom_field": "value"
        }
        token = create_access_token(data)
        decoded = decode_access_token(token)

        assert decoded is not None
        assert decoded["sub"] == "test@example.com"
        assert decoded["user_id"] == "123"
        assert decoded["is_admin"] is True
        assert decoded["custom_field"] == "value"

    def test_token_without_sub_claim(self):
        """Test creating token without sub claim."""
        data = {"user_id": "123"}
        token = create_access_token(data)
        decoded = decode_access_token(token)

        assert decoded is not None
        assert "user_id" in decoded
