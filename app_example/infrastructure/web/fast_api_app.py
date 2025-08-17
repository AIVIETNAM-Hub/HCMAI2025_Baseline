"""
FastAPI Application - Web framework integration

This is the INFRASTRUCTURE layer - contains framework-specific code.

Key principles:
- Depends on all inner layers
- Wires everything together
- Contains framework-specific configuration
- Handles HTTP routing and middleware
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any
import uvicorn

# Import from inner layers (dependency inversion)
from application.services.user_service import UserService
from interface.controllers.user_controller import UserController
from interface.repositories.memory_user_repo import MemoryUserRepository
from interface.repositories.file_user_repo import FileUserRepository
from infrastructure.config.settings import AppSettings


class FastAPIApp:
    """
    FastAPI application wrapper.

    This class:
    - Configures the FastAPI application
    - Sets up dependency injection
    - Defines HTTP routes
    - Handles the web framework concerns
    """

    def __init__(self, settings: AppSettings):
        self.settings = settings
        self.app = FastAPI(
            title="Clean Architecture User API",
            description="A minimal example of Clean Architecture with FastAPI",
            version="1.0.0",
            docs_url="/docs" if settings.enable_docs else None
        )

        # Set up dependencies (Dependency Injection)
        self._setup_dependencies()

        # Set up routes
        self._setup_routes()

    def _setup_dependencies(self):
        """Configure dependency injection"""
        # Choose repository implementation based on settings
        if self.settings.storage_type == "file":
            user_repository = FileUserRepository(self.settings.file_path)
        else:
            user_repository = MemoryUserRepository()

        # Wire up the layers
        self.user_service = UserService(user_repository)
        self.user_controller = UserController(self.user_service)

    def _setup_routes(self):
        """Set up HTTP routes"""

        @self.app.get("/")
        async def root():
            return {
                "message": "Clean Architecture User API",
                "docs": "/docs",
                "storage_type": self.settings.storage_type
            }

        @self.app.post(f"{self.settings.api_prefix}/users")
        async def create_user(request: Dict[str, Any]):
            """Create a new user"""
            result = await self.user_controller.create_user(request)
            return JSONResponse(
                content=result,
                status_code=result["status_code"]
            )

        @self.app.get(f"{self.settings.api_prefix}/users/{{user_id}}")
        async def get_user(user_id: int):
            """Get user by ID"""
            result = await self.user_controller.get_user(user_id)
            return JSONResponse(
                content=result,
                status_code=result["status_code"]
            )

        @self.app.get(f"{self.settings.api_prefix}/users")
        async def get_all_users():
            """Get all users"""
            result = await self.user_controller.get_all_users()
            return JSONResponse(
                content=result,
                status_code=result["status_code"]
            )

        @self.app.put(f"{self.settings.api_prefix}/users/{{user_id}}")
        async def update_user(user_id: int, request: Dict[str, Any]):
            """Update user"""
            result = await self.user_controller.update_user(user_id, request)
            return JSONResponse(
                content=result,
                status_code=result["status_code"]
            )

        @self.app.delete(f"{self.settings.api_prefix}/users/{{user_id}}")
        async def delete_user(user_id: int):
            """Delete user"""
            result = await self.user_controller.delete_user(user_id)
            return JSONResponse(
                content=result,
                status_code=result["status_code"]
            )

        @self.app.get(f"{self.settings.api_prefix}/users/search/domain/{{domain}}")
        async def search_users_by_domain(domain: str):
            """Search users by email domain"""
            result = await self.user_controller.search_users_by_domain(domain)
            return JSONResponse(
                content=result,
                status_code=result["status_code"]
            )

        # Health check endpoint
        @self.app.get("/health")
        async def health_check():
            user_count = await self.user_service.get_user_count()
            return {
                "status": "healthy",
                "storage_type": self.settings.storage_type,
                "total_users": user_count
            }

    def run(self):
        """Run the application"""
        uvicorn.run(
            self.app,
            host=self.settings.host,
            port=self.settings.port,
            reload=self.settings.debug
        )
