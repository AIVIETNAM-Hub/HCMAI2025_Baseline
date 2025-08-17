"""
User Controller - HTTP request/response handling

This is the INTERFACE layer - handles HTTP concerns and delegates to application services.

Key principles:
- Knows about HTTP requests/responses
- Depends on application services (inward dependency)
- Converts HTTP data to/from domain objects
- Handles HTTP-specific errors and status codes
"""

from typing import List, Dict, Any, Optional
from application.services.user_service import UserService
from domain.exceptions.user_exceptions import (
    UserNotFoundException,
    UserAlreadyExistsException,
    InvalidUserDataException
)


class UserController:
    """
    HTTP Controller for User operations.

    Responsibilities:
    - Handle HTTP requests/responses
    - Validate HTTP input data
    - Convert domain objects to HTTP responses
    - Handle domain exceptions and convert to HTTP errors
    """

    def __init__(self, user_service: UserService):
        """Dependency injection - depends on application service"""
        self._user_service = user_service

    async def create_user(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        HTTP endpoint: POST /users

        Converts HTTP request to domain operation
        """
        try:
            # Extract and validate HTTP request data
            username = request_data.get("username")
            email = request_data.get("email")
            full_name = request_data.get("full_name")

            if not username:
                return {
                    "success": False,
                    "error": "Username is required",
                    "status_code": 400
                }

            if not email:
                return {
                    "success": False,
                    "error": "Email is required",
                    "status_code": 400
                }

            if not full_name:
                return {
                    "success": False,
                    "error": "Full name is required",
                    "status_code": 400
                }

            # Delegate to application service
            user = await self._user_service.create_user(username, email, full_name)

            # Convert domain object to HTTP response
            return {
                "success": True,
                "data": user.to_dict(),
                "status_code": 201
            }

        except UserAlreadyExistsException as e:
            return {
                "success": False,
                "error": str(e),
                "status_code": 409  # Conflict
            }
        except InvalidUserDataException as e:
            return {
                "success": False,
                "error": str(e),
                "status_code": 400  # Bad Request
            }
        except Exception as e:
            return {
                "success": False,
                "error": "Internal server error",
                "status_code": 500
            }

    async def get_user(self, user_id: int) -> Dict[str, Any]:
        """
        HTTP endpoint: GET /users/{user_id}
        """
        try:
            user = await self._user_service.get_user_by_id(user_id)
            return {
                "success": True,
                "data": user.to_dict(),
                "status_code": 200
            }
        except UserNotFoundException as e:
            return {
                "success": False,
                "error": str(e),
                "status_code": 404  # Not Found
            }
        except Exception as e:
            return {
                "success": False,
                "error": "Internal server error",
                "status_code": 500
            }

    async def get_all_users(self) -> Dict[str, Any]:
        """
        HTTP endpoint: GET /users
        """
        try:
            users = await self._user_service.get_all_users()
            return {
                "success": True,
                "data": [user.to_dict() for user in users],
                "count": len(users),
                "status_code": 200
            }
        except Exception as e:
            return {
                "success": False,
                "error": "Internal server error",
                "status_code": 500
            }

    async def update_user(self, user_id: int, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        HTTP endpoint: PUT /users/{user_id}
        """
        try:
            # Extract optional update fields
            full_name = request_data.get("full_name")
            email = request_data.get("email")

            # Delegate to application service
            user = await self._user_service.update_user(
                user_id=user_id,
                full_name=full_name,
                email=email
            )

            return {
                "success": True,
                "data": user.to_dict(),
                "status_code": 200
            }

        except UserNotFoundException as e:
            return {
                "success": False,
                "error": str(e),
                "status_code": 404
            }
        except InvalidUserDataException as e:
            return {
                "success": False,
                "error": str(e),
                "status_code": 400
            }
        except Exception as e:
            return {
                "success": False,
                "error": "Internal server error",
                "status_code": 500
            }

    async def delete_user(self, user_id: int) -> Dict[str, Any]:
        """
        HTTP endpoint: DELETE /users/{user_id}
        """
        try:
            success = await self._user_service.delete_user(user_id)
            return {
                "success": True,
                "message": f"User {user_id} deleted successfully",
                "status_code": 200
            }
        except UserNotFoundException as e:
            return {
                "success": False,
                "error": str(e),
                "status_code": 404
            }
        except Exception as e:
            return {
                "success": False,
                "error": "Internal server error",
                "status_code": 500
            }

    async def search_users_by_domain(self, domain: str) -> Dict[str, Any]:
        """
        HTTP endpoint: GET /users/search/domain/{domain}
        """
        try:
            users = await self._user_service.search_users_by_email_domain(domain)
            return {
                "success": True,
                "data": [user.to_dict() for user in users],
                "count": len(users),
                "search_domain": domain,
                "status_code": 200
            }
        except Exception as e:
            return {
                "success": False,
                "error": "Internal server error",
                "status_code": 500
            }
