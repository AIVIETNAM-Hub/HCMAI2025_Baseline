"""
Repository Interface - Contract for data access

This is the APPLICATION layer defining what it needs from the data layer.
The actual implementation will be in the INTERFACE layer.

Key principle: Application layer defines the contract, infrastructure implements it.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.user import User


class UserRepositoryInterface(ABC):
    """
    Abstract repository interface for User data access.

    This interface:
    - Lives in the Application layer
    - Defines what the business logic needs
    - Is implemented by concrete repositories in outer layers
    - Follows the Dependency Inversion Principle
    """

    @abstractmethod
    async def save(self, user: User) -> User:
        """Save a user and return the saved user with any generated fields"""
        pass

    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get a user by their ID"""
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get a user by their username"""
        pass

    @abstractmethod
    async def get_all(self) -> List[User]:
        """Get all users"""
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        """Update an existing user"""
        pass

    @abstractmethod
    async def delete(self, user_id: int) -> bool:
        """Delete a user by ID. Returns True if deleted, False if not found"""
        pass

    @abstractmethod
    async def exists_by_username(self, username: str) -> bool:
        """Check if a user exists with the given username"""
        pass

    @abstractmethod
    async def count(self) -> int:
        """Get total number of users"""
        pass
