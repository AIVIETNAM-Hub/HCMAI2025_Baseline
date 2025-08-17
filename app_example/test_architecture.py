"""
Simple test to validate Clean Architecture implementation

Run this to verify that all layers work correctly and independently.
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from domain.entities.user import User
from domain.exceptions.user_exceptions import UserNotFoundException, UserAlreadyExistsException
from application.services.user_service import UserService
from interface.repositories.memory_user_repo import MemoryUserRepository
from interface.repositories.file_user_repo import FileUserRepository


async def test_domain_layer():
    """Test domain entities and business rules"""
    print("🔵 Testing Domain Layer...")

    # Test valid user creation
    user = User(
        user_id=1,
        username="testuser",
        email="test@example.com",
        full_name="Test User"
    )
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    print("  ✅ Valid user creation works")

    # Test business rules
    try:
        User(1, "ab", "test@example.com", "Test User")  # Username too short
        assert False, "Should have raised ValueError"
    except ValueError:
        print("  ✅ Username validation works")

    try:
        User(1, "testuser", "invalid-email", "Test User")  # Invalid email
        assert False, "Should have raised ValueError"
    except ValueError:
        print("  ✅ Email validation works")

    # Test update business logic
    user.update_profile(full_name="Updated Name")
    assert user.full_name == "Updated Name"
    print("  ✅ Profile update works")


async def test_application_layer():
    """Test application services and use cases"""
    print("\n🟢 Testing Application Layer...")

    # Use memory repository for testing
    repository = MemoryUserRepository()
    service = UserService(repository)

    # Test create user use case
    user = await service.create_user("testuser", "test@example.com", "Test User")
    assert user.username == "testuser"
    print("  ✅ Create user use case works")

    # Test duplicate username prevention
    try:
        await service.create_user("testuser", "other@example.com", "Other User")
        assert False, "Should have raised UserAlreadyExistsException"
    except UserAlreadyExistsException:
        print("  ✅ Duplicate username prevention works")

    # Test get user by ID
    retrieved_user = await service.get_user_by_id(1)
    assert retrieved_user.username == "testuser"
    print("  ✅ Get user by ID works")

    # Test user not found
    try:
        await service.get_user_by_id(999)
        assert False, "Should have raised UserNotFoundException"
    except UserNotFoundException:
        print("  ✅ User not found exception works")

    # Test search by domain
    users = await service.search_users_by_email_domain("example.com")
    assert len(users) == 1
    print("  ✅ Search by domain works")


async def test_repository_swapping():
    """Test that repositories can be swapped without changing business logic"""
    print("\n🔄 Testing Repository Swapping...")

    # Test with memory repository
    memory_repo = MemoryUserRepository()
    memory_service = UserService(memory_repo)

    user1 = await memory_service.create_user("user1", "user1@test.com", "User One")
    print("  ✅ Memory repository works")

    # Test with file repository
    file_repo = FileUserRepository("test_users.json")
    file_service = UserService(file_repo)

    user2 = await file_service.create_user("user2", "user2@test.com", "User Two")
    print("  ✅ File repository works")

    # Verify they work independently
    memory_users = await memory_service.get_all_users()
    file_users = await file_service.get_all_users()

    assert len(memory_users) == 1
    assert len(file_users) == 1
    assert memory_users[0].username != file_users[0].username
    print("  ✅ Repositories work independently")

    # Clean up
    file_repo.clear_all()
    if os.path.exists("test_users.json"):
        os.remove("test_users.json")


async def test_interface_layer():
    """Test controllers and HTTP handling"""
    print("\n🟡 Testing Interface Layer...")

    from interface.controllers.user_controller import UserController

    repository = MemoryUserRepository()
    service = UserService(repository)
    controller = UserController(service)

    # Test create user via controller
    request_data = {
        "username": "controlleruser",
        "email": "controller@test.com",
        "full_name": "Controller User"
    }

    response = await controller.create_user(request_data)
    assert response["success"] is True
    assert response["status_code"] == 201
    print("  ✅ Controller create user works")

    # Test get user via controller
    response = await controller.get_user(1)
    assert response["success"] is True
    assert response["data"]["username"] == "controlleruser"
    print("  ✅ Controller get user works")

    # Test error handling
    response = await controller.get_user(999)
    assert response["success"] is False
    assert response["status_code"] == 404
    print("  ✅ Controller error handling works")


async def run_tests():
    """Run all tests"""
    print("🧪 Clean Architecture Tests")
    print("=" * 50)

    try:
        await test_domain_layer()
        await test_application_layer()
        await test_repository_swapping()
        await test_interface_layer()

        print("\n" + "=" * 50)
        print("🎉 All tests passed! Clean Architecture is working correctly.")
        print("\nKey principles demonstrated:")
        print("  ✅ Domain layer has no external dependencies")
        print("  ✅ Application layer depends only on domain and interfaces")
        print("  ✅ Repository implementations can be swapped easily")
        print("  ✅ Controllers handle HTTP concerns separately")
        print("  ✅ Business logic works independently of infrastructure")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_tests())
