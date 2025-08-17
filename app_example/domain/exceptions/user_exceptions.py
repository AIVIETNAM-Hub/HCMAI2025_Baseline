"""
Domain Exceptions - Business-specific errors

These represent business rule violations, not technical errors.
"""


class DomainException(Exception):
    """Base exception for all domain-related errors"""
    pass


class UserNotFoundException(DomainException):
    """Raised when a user cannot be found"""

    def __init__(self, user_id: int):
        self.user_id = user_id
        super().__init__(f"User with ID {user_id} not found")


class UserAlreadyExistsException(DomainException):
    """Raised when trying to create a user that already exists"""

    def __init__(self, username: str):
        self.username = username
        super().__init__(f"User with username '{username}' already exists")


class InvalidUserDataException(DomainException):
    """Raised when user data violates business rules"""

    def __init__(self, message: str):
        super().__init__(f"Invalid user data: {message}")


class UserValidationException(DomainException):
    """Raised when user data fails validation"""

    def __init__(self, field: str, message: str):
        self.field = field
        super().__init__(f"Validation error for {field}: {message}")
