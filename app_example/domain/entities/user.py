"""
Domain Entities - Pure business objects with no external dependencies

This is the CORE of Clean Architecture - contains only business logic.
"""

from datetime import datetime
from typing import Optional


class User:
    """
    User domain entity - represents a user in our business domain.

    Key principles:
    - No database dependencies
    - No framework dependencies
    - Pure business logic only
    - Enforces business rules
    """

    def __init__(
        self,
        user_id: int,
        username: str,
        email: str,
        full_name: str,
        created_at: Optional[datetime] = None
    ):
        # Enforce business rules
        if not username or len(username.strip()) < 3:
            raise ValueError("Username must be at least 3 characters long")

        if not email or "@" not in email:
            raise ValueError("Email must be a valid email address")

        if not full_name or len(full_name.strip()) < 2:
            raise ValueError("Full name must be at least 2 characters long")

        self.user_id = user_id
        self.username = username.strip()
        self.email = email.lower().strip()
        self.full_name = full_name.strip()
        self.created_at = created_at or datetime.now()
        self.updated_at = datetime.now()

    def update_profile(self, full_name: Optional[str] = None, email: Optional[str] = None):
        """Business logic for updating user profile"""
        if full_name is not None:
            if len(full_name.strip()) < 2:
                raise ValueError("Full name must be at least 2 characters long")
            self.full_name = full_name.strip()

        if email is not None:
            if "@" not in email:
                raise ValueError("Email must be a valid email address")
            self.email = email.lower().strip()

        self.updated_at = datetime.now()

    def is_email_valid(self) -> bool:
        """Domain business rule for email validation"""
        return "@" in self.email and "." in self.email.split("@")[1]

    def get_display_name(self) -> str:
        """Business logic for how names are displayed"""
        return f"{self.full_name} (@{self.username})"

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Create User from dictionary"""
        user = cls(
            user_id=data["user_id"],
            username=data["username"],
            email=data["email"],
            full_name=data["full_name"],
            created_at=datetime.fromisoformat(data["created_at"])
        )
        user.updated_at = datetime.fromisoformat(data["updated_at"])
        return user

    def __str__(self) -> str:
        return f"User(id={self.user_id}, username={self.username}, email={self.email})"

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other) -> bool:
        if not isinstance(other, User):
            return False
        return self.user_id == other.user_id
