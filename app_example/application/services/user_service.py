"""
User Service - Application layer business logic

This contains the USE CASES of our system.
Key principles:
- No knowledge of HTTP, databases, or frameworks
- Depends only on domain entities and repository interfaces
- Contains business workflow logic
- Enforces business rules through domain entities
"""

from typing import List, Optional
from domain.entities.user import User
from domain.exceptions.user_exceptions import (
    UserNotFoundException,
    UserAlreadyExistsException,
    InvalidUserDataException
)
from application.interfaces.user_repository import UserRepositoryInterface


class UserService:
    """
    User Service - Contains all business use cases for user management.

    This is the APPLICATION layer - pure business logic with no external dependencies.
    """

    def __init__(self, user_repository: UserRepositoryInterface):
        """
        Dependency injection - we depend on the interface, not the implementation.
        This follows the Dependency Inversion Principle.
        """
        self._user_repository = user_repository

    async def create_user(
        self,
        username: str,
        email: str,
        full_name: str
    ) -> User:
        """
        Use Case: Create a new user

        Business rules:
        1. Username must be unique
        2. User data must be valid (enforced by User entity)
        3. Return the created user
        """
        # Check if user already exists (business rule)
        if await self._user_repository.exists_by_username(username):
            raise UserAlreadyExistsException(username)

        # Generate new user ID (simple incrementing ID for this example)
        user_count = await self._user_repository.count()
        new_user_id = user_count + 1

        try:
            # Create domain entity (validates business rules)
            user = User(
                user_id=new_user_id,
                username=username,
                email=email,
                full_name=full_name
            )
        except ValueError as e:
            raise InvalidUserDataException(str(e))

        # Save through repository interface
        return await self._user_repository.save(user)

    async def get_user_by_id(self, user_id: int) -> User:
        """
        Use Case: Get user by ID

        Business rule: Must exist or raise exception
        """
        user = await self._user_repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundException(user_id)
        return user

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Use Case: Get user by username

        Returns None if not found (different business rule than get_by_id)
        """
        return await self._user_repository.get_by_username(username)

    async def get_all_users(self) -> List[User]:
        """
        Use Case: List all users
        """
        return await self._user_repository.get_all()

    async def update_user(
        self,
        user_id: int,
        full_name: Optional[str] = None,
        email: Optional[str] = None
    ) -> User:
        """
        Use Case: Update user profile

        Business rules:
        1. User must exist
        2. Updated data must be valid
        3. Username cannot be changed (business rule)
        """
        # Get existing user
        user = await self.get_user_by_id(user_id)  # Raises UserNotFoundException if not found

        try:
            # Update using domain entity business logic
            user.update_profile(full_name=full_name, email=email)
        except ValueError as e:
            raise InvalidUserDataException(str(e))

        # Save updated user
        return await self._user_repository.update(user)

    async def delete_user(self, user_id: int) -> bool:
        """
        Use Case: Delete user

        Business rule: Return success status
        """
        # Check if user exists first (business rule - be explicit about what we're deleting)
        await self.get_user_by_id(user_id)  # Raises UserNotFoundException if not found

        return await self._user_repository.delete(user_id)

    async def get_user_count(self) -> int:
        """
        Use Case: Get total number of users
        """
        return await self._user_repository.count()

    async def search_users_by_email_domain(self, domain: str) -> List[User]:
        """
        Use Case: Search users by email domain

        Business logic: Filter users by email domain
        """
        all_users = await self._user_repository.get_all()
        return [
            user for user in all_users
            if user.email.endswith(f"@{domain}")
        ]

    async def get_users_created_after(self, date_threshold) -> List[User]:
        """
        Use Case: Get users created after a certain date

        Business logic: Filter by creation date
        """
        all_users = await self._user_repository.get_all()
        return [
            user for user in all_users
            if user.created_at > date_threshold
        ]
