"""Authentication service: password hashing, credential checks, seeding."""

import hashlib
import hmac
import os
from typing import Optional

from src.db import execute, fetch_one
from src.models.user import User


def _hash_password(password: str) -> str:
    """Hash a password as ``salt$sha256_hex`` using a random 16-byte salt."""
    salt = os.urandom(16).hex()
    digest = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return f"{salt}${digest}"


def _verify_password(password: str, stored: str) -> bool:
    """Verify a password against a ``salt$hash`` string in constant time."""
    try:
        salt, expected = stored.split("$", 1)
    except ValueError:
        return False
    actual = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return hmac.compare_digest(actual, expected)


class AuthService:
    """Handles authentication and default user seeding."""

    def verify_credentials(self, username: str, password: str) -> Optional[User]:
        """Return the matching User or None when credentials are invalid."""
        user = self.get_user_by_username(username)
        if user is None:
            return None
        if not _verify_password(password, user.password_hash):
            return None
        return user

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Fetch a user by username, or None if it does not exist."""
        row = fetch_one("SELECT * FROM users WHERE username = ?", (username,))
        if row is None:
            return None
        return User(**dict(row))

    def create_user(self, username: str, password: str, role: str, full_name: str) -> int:
        """Create a new user and return its id."""
        return execute(
            "INSERT INTO users (username, password_hash, role, full_name) VALUES (?, ?, ?, ?)",
            (username, _hash_password(password), role, full_name),
        )

    def seed_default_users(self) -> None:
        """Insert the default users if they do not exist yet. Idempotent."""
        defaults = [
            ("admin", "admin123", "admin", "Administrador del Sistema"),
            ("dispatcher", "dispatcher123", "dispatcher", "Despachador"),
            ("consultor", "consultor123", "consultor", "Consultor"),
        ]
        for username, password, role, full_name in defaults:
            if self.get_user_by_username(username) is None:
                self.create_user(username, password, role, full_name)


auth_service = AuthService()
