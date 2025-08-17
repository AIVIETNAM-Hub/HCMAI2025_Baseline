"""
FastAPI Application Entry Point

This creates the FastAPI app instance that can be imported by uvicorn.
Fixes the uvicorn reload warning by providing a proper app instance.
"""

import sys
import os
from typing import Dict, Any

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Import Clean Architecture layers
from application.services.user_service import UserService
from interface.controllers.user_controller import UserController
from interface.repositories.memory_user_repo import MemoryUserRepository
from interface.repositories.file_user_repo import FileUserRepository
from infrastructure.config.settings import AppSettings


# Pydantic models for request/response
class UserCreateRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Username (3-50 characters)")
    email: str = Field(..., description="Valid email address")
    full_name: str = Field(..., min_length=2, max_length=100, description="Full name (2-100 characters)")

class UserUpdateRequest(BaseModel):
    full_name: str | None = Field(None, min_length=2, max_length=100, description="Full name (2-100 characters)")
    email: str | None = Field(None, description="Valid email address")

class UserResponse(BaseModel):
    user_id: int
    username: str
    email: str
    full_name: str
    created_at: str
    updated_at: str

class UsersListResponse(BaseModel):
    users: list[UserResponse]
    total: int

class MessageResponse(BaseModel):
    message: str
    success: bool = True


# Initialize settings and dependencies
settings = AppSettings()

# Choose repository implementation based on settings
if settings.storage_type == "file":
    user_repository = FileUserRepository(settings.file_path)
else:
    user_repository = MemoryUserRepository()

# Wire up the clean architecture layers
user_service = UserService(user_repository)
user_controller = UserController(user_service)

# Create FastAPI app instance
app = FastAPI(
    title="Clean Architecture User Management API",
    description="A demonstration of Clean Architecture principles with comprehensive CRUD operations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# Root endpoint
@app.get("/", response_model=Dict[str, Any])
async def root():
    """API information and health check"""
    user_count = await user_service.get_user_count()
    return {
        "message": "Clean Architecture User Management API",
        "version": "1.0.0",
        "docs": "/docs",
        "storage_type": settings.storage_type,
        "total_users": user_count,
        "endpoints": {
            "create_user": "POST /users",
            "get_all_users": "GET /users",
            "get_user": "GET /users/{user_id}",
            "update_user": "PUT /users/{user_id}",
            "delete_user": "DELETE /users/{user_id}",
            "search_by_domain": "GET /users/search/domain/{domain}"
        }
    }


# CRUD Endpoints

@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreateRequest):
    """
    Create a new user

    - **username**: Must be unique and 3-50 characters
    - **email**: Must be a valid email address
    - **full_name**: Must be 2-100 characters

    Returns the created user with generated ID and timestamps.
    """
    try:
        result = await user_controller.create_user(user_data.dict())

        if not result["success"]:
            raise HTTPException(
                status_code=result["status_code"],
                detail=result["error"]
            )

        return UserResponse(**result["data"])

    except Exception as e:
        if "already exists" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )
        elif "invalid" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )


@app.get("/users", response_model=UsersListResponse)
async def get_all_users():
    """
    Retrieve all users

    Returns a list of all users in the system with their complete information.
    """
    try:
        result = await user_controller.get_all_users()

        if not result["success"]:
            raise HTTPException(
                status_code=result["status_code"],
                detail=result["error"]
            )

        users = [UserResponse(**user) for user in result["data"]]
        return UsersListResponse(users=users, total=len(users))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """
    Retrieve a specific user by ID

    - **user_id**: The unique identifier of the user

    Returns the user information if found.
    """
    try:
        result = await user_controller.get_user(user_id)

        if not result["success"]:
            raise HTTPException(
                status_code=result["status_code"],
                detail=result["error"]
            )

        return UserResponse(**result["data"])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@app.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_data: UserUpdateRequest):
    """
    Update an existing user

    - **user_id**: The unique identifier of the user
    - **full_name**: New full name (optional)
    - **email**: New email address (optional)

    Note: Username cannot be changed for security reasons.
    Returns the updated user information.
    """
    try:
        # Only include non-None fields in the update
        update_data = {k: v for k, v in user_data.dict().items() if v is not None}

        result = await user_controller.update_user(user_id, update_data)

        if not result["success"]:
            raise HTTPException(
                status_code=result["status_code"],
                detail=result["error"]
            )

        return UserResponse(**result["data"])

    except HTTPException:
        raise
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        elif "invalid" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )


@app.delete("/users/{user_id}", response_model=MessageResponse)
async def delete_user(user_id: int):
    """
    Delete a user

    - **user_id**: The unique identifier of the user to delete

    Returns a success message if the user was deleted.
    """
    try:
        result = await user_controller.delete_user(user_id)

        if not result["success"]:
            raise HTTPException(
                status_code=result["status_code"],
                detail=result["error"]
            )

        return MessageResponse(message=result["message"], success=True)

    except HTTPException:
        raise
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )


# Additional search endpoint
@app.get("/users/search/domain/{domain}", response_model=UsersListResponse)
async def search_users_by_email_domain(domain: str):
    """
    Search users by email domain

    - **domain**: Email domain to search for (e.g., "example.com")

    Returns all users with email addresses ending with @{domain}.
    """
    try:
        result = await user_controller.search_users_by_domain(domain)

        if not result["success"]:
            raise HTTPException(
                status_code=result["status_code"],
                detail=result["error"]
            )

        users = [UserResponse(**user) for user in result["data"]]
        return UsersListResponse(users=users, total=len(users))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


# Health check endpoint
@app.get("/health")
async def health_check():
    """System health check"""
    try:
        user_count = await user_service.get_user_count()
        return {
            "status": "healthy",
            "storage_type": settings.storage_type,
            "total_users": user_count,
            "timestamp": "2025-01-01T00:00:00Z"  # You could use datetime.now() here
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unavailable"
        )


# For running the server directly
def run_server():
    """Run the FastAPI server using uvicorn"""
    import uvicorn
    uvicorn.run(
        "app:app",  # Import string format to fix the reload warning
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )


if __name__ == "__main__":
    print("🚀 Starting Clean Architecture FastAPI Server...")
    print(f"   Storage: {settings.storage_type}")
    print(f"   Server: http://{settings.host}:{settings.port}")
    print(f"   API Docs: http://{settings.host}:{settings.port}/docs")
    print(f"   ReDoc: http://{settings.host}:{settings.port}/redoc")
    run_server()
