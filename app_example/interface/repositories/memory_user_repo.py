"""
Memory User Repository - In-memory implementation

This is a concrete implementation of UserRepositoryInterface.
It stores data in memory - perfect for testing and demos.

Key principles:
- Implements the interface defined in the application layer
- Contains no business logic - just data storage/retrieval
- Can be easily swapped with other implementations
"""

from typing import List, Optional, Dict
from application.interfaces.user_repository import UserRepositoryInterface
from domain.entities.user import User


class MemoryUserRepository(UserRepositoryInterface):
    """
    In-memory implementation of user repository.

    Great for:
    - Testing
    - Development
    - Demos
    - Quick prototyping
    """

    def __init__(self):
        """Initialize with empty storage"""
        self._users: Dict[int, User] = {}
        self._username_index: Dict[str, int] = {}  # username -> user_id mapping

    async def save(self, user: User) -> User:
        """Save user to memory"""
        self._users[user.user_id] = user
        self._username_index[user.username] = user.user_id
        return user

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID from memory"""
        return self._users.get(user_id)

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username from memory"""
        user_id = self._username_index.get(username)
        if user_id is None:
            return None
        return self._users.get(user_id)

    async def get_all(self) -> List[User]:
        """Get all users from memory"""
        return list(self._users.values())

    async def update(self, user: User) -> User:
        """Update user in memory"""
        if user.user_id not in self._users:
            raise ValueError(f"User with ID {user.user_id} not found")

        # Update username index if username changed
        old_user = self._users[user.user_id]
        if old_user.username != user.username:
            # Remove old username mapping
            del self._username_index[old_user.username]
            # Add new username mapping
            self._username_index[user.username] = user.user_id

        self._users[user.user_id] = user
        return user

    async def delete(self, user_id: int) -> bool:
        """Delete user from memory"""
        if user_id not in self._users:
            return False

        user = self._users[user_id]
        del self._users[user_id]
        del self._username_index[user.username]
        return True

    async def exists_by_username(self, username: str) -> bool:
        """Check if user exists by username"""
        return username in self._username_index

    async def count(self) -> int:
        """Get total number of users"""
        return len(self._users)

    # Additional utility methods for testing/debugging
    def clear_all(self):
        """Clear all data (useful for testing)"""
        self._users.clear()
        self._username_index.clear()

    def get_storage_info(self) -> Dict[str, int]:
        """Get storage statistics"""
        return {
            "user_count": len(self._users),
            "username_index_size": len(self._username_index)
        }
