# Minimal Clean Architecture Example

This is a simplified example to demonstrate Clean Architecture principles using a basic **User Management System**.

## 🎯 What This Example Shows

- **Domain Layer**: Pure business entities and rules
- **Application Layer**: Use cases and business logic
- **Interface Layer**: Controllers and repository abstractions
- **Infrastructure Layer**: Database implementations and web framework

## 📁 Folder Structure

```
app_example/
├── README.md                 # This file
├── domain/                   # 🔵 CORE - Business entities and rules
│   ├── __init__.py
│   ├── entities/
│   │   ├── __init__.py
│   │   └── user.py          # User entity (pure business object)
│   └── exceptions/
│       ├── __init__.py
│       └── user_exceptions.py # Domain-specific errors
├── application/              # 🟢 USE CASES - Business logic
│   ├── __init__.py
│   ├── interfaces/
│   │   ├── __init__.py
│   │   └── user_repository.py # Repository contract
│   └── services/
│       ├── __init__.py
│       └── user_service.py   # Business use cases
├── interface/                # 🟡 ADAPTERS - Controllers and gateways
│   ├── __init__.py
│   ├── controllers/
│   │   ├── __init__.py
│   │   └── user_controller.py # HTTP request handling
│   └── repositories/
│       ├── __init__.py
│       ├── memory_user_repo.py # In-memory implementation
│       └── file_user_repo.py   # File-based implementation
├── infrastructure/           # 🔴 EXTERNAL - Framework and drivers
│   ├── __init__.py
│   ├── web/
│   │   ├── __init__.py
│   │   └── fast_api_app.py   # FastAPI application
│   └── config/
│       ├── __init__.py
│       └── settings.py       # Configuration
└── main.py                   # Application entry point
```

## 🔄 Clean Architecture Layers

### 1. Domain Layer (Center - Blue 🔵)
- **Pure business logic** - no external dependencies
- **Entities**: Core business objects (`User`)
- **Business rules**: Validation, invariants
- **Domain exceptions**: Business-specific errors

### 2. Application Layer (Green 🟢)
- **Use cases** - what the system can do
- **Repository interfaces** - contracts for data access
- **Business services** - orchestrate domain entities
- **No knowledge of HTTP, databases, or frameworks**

### 3. Interface Layer (Yellow 🟡)
- **Controllers** - handle HTTP requests/responses
- **Repository implementations** - concrete data access
- **Presenters** - format output for external systems
- **Depends inward only** - knows about Application + Domain

### 4. Infrastructure Layer (Red 🔴)
- **Frameworks** - FastAPI, databases, external APIs
- **Configuration** - environment settings
- **Entry points** - main application startup
- **Depends on everything** - wires all layers together

## 🚀 How to Run

```bash
# From the app_example directory
python main.py
```

## 📋 Example API Endpoints

- `POST /users` - Create a new user
- `GET /users/{user_id}` - Get user by ID
- `GET /users` - List all users
- `PUT /users/{user_id}` - Update user
- `DELETE /users/{user_id}` - Delete user

## 🧪 Testing the Flow

1. **HTTP Request** hits FastAPI (`infrastructure/web/fast_api_app.py`)
2. **Router** calls **Controller** (`interface/controllers/user_controller.py`)
3. **Controller** calls **Service** (`application/services/user_service.py`)
4. **Service** uses **Repository Interface** (`application/interfaces/user_repository.py`)
5. **Concrete Repository** (`interface/repositories/memory_user_repo.py`) handles data
6. **Domain Entity** (`domain/entities/user.py`) enforces business rules

## 🔑 Key Clean Architecture Principles Demonstrated

### ✅ Dependency Rule
- Outer layers depend on inner layers
- Inner layers never import from outer layers
- Domain has zero external dependencies

### ✅ Independence
- Business logic independent of UI, database, frameworks
- Can swap repository implementations (memory ↔ file ↔ database)
- Can change web framework without touching business logic

### ✅ Testability
- Domain logic testable without external dependencies
- Services testable with mock repositories
- Controllers testable with mock services

## 💡 Benefits You'll See

1. **Easy to test** - Mock dependencies at each layer
2. **Easy to change** - Swap implementations without breaking business logic
3. **Clear separation** - Each layer has a single responsibility
4. **Independent development** - Teams can work on different layers
5. **Framework agnostic** - Business logic doesn't depend on FastAPI

## 🎓 Learning Path

1. Start with `domain/entities/user.py` - see pure business logic
2. Look at `application/services/user_service.py` - see use cases
3. Check `interface/controllers/user_controller.py` - see request handling
4. Explore `interface/repositories/` - see different implementations
5. Review `main.py` - see how everything connects

## 🔄 Try Swapping Implementations

The example includes two repository implementations:
- `MemoryUserRepository` - stores in memory
- `FileUserRepository` - stores in JSON file

Change the repository in `main.py` to see how easily you can swap implementations without changing any business logic!

```python
# In main.py, change this line:
user_repository = MemoryUserRepository()  # In-memory storage
# To this:
user_repository = FileUserRepository("users.json")  # File storage
```

The API works exactly the same - that's Clean Architecture in action! 🎉
