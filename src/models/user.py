"""User data model."""

from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    """A registered application user."""

    id: Optional[int] = None
    username: str
    password_hash: str
    role: str
    full_name: str

    def model_dump_for_db(self) -> dict:
        """Return field values ready for an INSERT, excluding the id."""
        return self.model_dump(exclude={"id"})
