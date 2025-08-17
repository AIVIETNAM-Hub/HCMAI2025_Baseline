"""
File User Repository - JSON file-based implementation

This demonstrates how easily you can swap repository implementations.
Stores data in a JSON file on disk.

Key principles:
- Same interface as MemoryUserRepository
- Different storage mechanism (file vs memory)
- Business logic remains unchanged
- Demonstrates Clean Architecture flexibility
"""

import json
import os
from typing import List, Optional
from application.interfaces.user_repository import UserRepositoryInterface
from domain.entities.user import User


class FileUserRepository(UserRepositoryInterface):
    """
    File-based implementation of user repository.

    Stores users in a JSON file on disk.
    Great for demonstrating how Clean Architecture enables
    swapping implementations without changing business logic.
    """

    def __init__(self, file_path: str = "users.json"):
        """Initialize with file path"""
        self.file_path = file_path
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Create empty JSON file if it doesn't exist"""
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                json.dump([], f)

    def _load_users(self) -> List[User]:
        """Load all users from file"""
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                return [User.from_dict(user_data) for user_data in data]
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_users(self, users: List[User]):
        """Save all users to file"""
        with open(self.file_path, 'w') as f:
            data = [user.to_dict() for user in users]
            json.dump(data, f, indent=2)

    async def save(self, user: User) -> User:
        """Save user to file"""
        users = self._load_users()

        # Check if user already exists and update, otherwise add
        for i, existing_user in enumerate(users):
            if existing_user.user_id == user.user_id:
                users[i] = user
                break
        else:
            users.append(user)

        self._save_users(users)
        return user

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID from file"""
        users = self._load_users()
        for user in users:
            if user.user_id == user_id:
                return user
        return None

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username from file"""
        users = self._load_users()
        for user in users:
            if user.username == username:
                return user
        return None

    async def get_all(self) -> List[User]:
        """Get all users from file"""
        return self._load_users()

    async def update(self, user: User) -> User:
        """Update user in file"""
        users = self._load_users()

        for i, existing_user in enumerate(users):
            if existing_user.user_id == user.user_id:
                users[i] = user
                self._save_users(users)
                return user

        raise ValueError(f"User with ID {user.user_id} not found")

    async def delete(self, user_id: int) -> bool:
        """Delete user from file"""
        users = self._load_users()

        for i, user in enumerate(users):
            if user.user_id == user_id:
                del users[i]
                self._save_users(users)
                return True

        return False

    async def exists_by_username(self, username: str) -> bool:
        """Check if user exists by username"""
        users = self._load_users()
        return any(user.username == username for user in users)

    async def count(self) -> int:
        """Get total number of users"""
        users = self._load_users()
        return len(users)

    # Additional utility methods
    def clear_all(self):
        """Clear all data (useful for testing)"""
        with open(self.file_path, 'w') as f:
            json.dump([], f)

    def get_file_size(self) -> int:
        """Get file size in bytes"""
        try:
            return os.path.getsize(self.file_path)
        except FileNotFoundError:
            return 0
