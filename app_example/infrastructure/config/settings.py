"""
Application Settings - Configuration management

This is in the INFRASTRUCTURE layer because it deals with external configuration.
"""

from typing import Optional


class AppSettings:
    """
    Application configuration settings.

    In a real application, this would load from:
    - Environment variables
    - Configuration files
    - Command line arguments
    - etc.
    """

    def __init__(self):
        # Server settings
        self.host: str = "localhost"
        self.port: int = 8000
        self.debug: bool = True

        # Storage settings
        self.storage_type: str = "memory"  # "memory" or "file"
        self.file_path: str = "users.json"

        # API settings
        self.api_prefix: str = "/api/v1"
        self.enable_docs: bool = True

        # Logging
        self.log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "AppSettings":
        """Create settings from environment variables (placeholder)"""
        settings = cls()
        # In a real app, you'd read from os.environ here
        return settings
