# Clean Architecture Visual Guide

## 🎯 Architecture Layers Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    🔴 INFRASTRUCTURE                        │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                 🟡 INTERFACE                        │    │
│  │  ┌─────────────────────────────────────────────┐    │    │
│  │  │               🟢 APPLICATION                │    │    │
│  │  │  ┌─────────────────────────────────────┐    │    │    │
│  │  │  │          🔵 DOMAIN                  │    │    │    │
│  │  │  │                                     │    │     │    │
│  │  │  │  • User Entity                      │    │    │    │
│  │  │  │  • Business Rules                   │    │    │    │
│  │  │  │  • Domain Exceptions                │    │    │    │
│  │  │  │                                     │    │    │    │
│  │  │  └─────────────────────────────────────┘    │    │    │
│  │  │                                             │    │    │
│  │  │  • User Service (Use Cases)                 │    │    │
│  │  │  • Repository Interfaces                    │    │    │
│  │  │  • Business Logic                           │    │    │
│  │  │                                             │    │    │
│  │  └─────────────────────────────────────────────┘    │    │
│  │                                                     │    │
│  │  • Controllers (HTTP handling)                      │    │
│  │  • Repository Implementations                       │    │
│  │  • Data Access Logic                                │    │
│  │                                                     │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│  • FastAPI Application                                      │
│  • Configuration                                            │
│  • External Services                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Dependency Flow

```
HTTP Request
     ↓
FastAPI Router (🔴 Infrastructure)
     ↓
User Controller (🟡 Interface)
     ↓
User Service (🟢 Application)
     ↓
Repository Interface (🟢 Application)
     ↓
Concrete Repository (🟡 Interface)
     ↓
Storage (Memory/File/Database)
```

## 📁 File Structure Mapping

```
app_example/
├── domain/ ...................... 🔵 DOMAIN LAYER
│   ├── entities/
│   │   └── user.py .............. Pure business entity
│   └── exceptions/
│       └── user_exceptions.py ... Business errors
│
├── application/ ................. 🟢 APPLICATION LAYER
│   ├── interfaces/
│   │   └── user_repository.py ... Repository contract
│   └── services/
│       └── user_service.py ...... Business use cases
│
├── interface/ ................... 🟡 INTERFACE LAYER
│   ├── controllers/
│   │   └── user_controller.py ... HTTP request handling
│   └── repositories/
│       ├── memory_user_repo.py .. In-memory implementation
│       └── file_user_repo.py .... File-based implementation
│
├── infrastructure/ .............. 🔴 INFRASTRUCTURE LAYER
│   ├── web/
│   │   └── fast_api_app.py ...... FastAPI application
│   └── config/
│       └── settings.py .......... Configuration
│
├── main.py ...................... Entry point & DI setup
├── test_architecture.py ........ Validation tests
└── README.md .................... This guide
```

## 🎯 Key Principles Demonstrated

### 1. Dependency Rule ✅
- **Inner layers** never depend on **outer layers**
- **Outer layers** can depend on **inner layers**
- Dependencies point **inward only**

```
Domain ← Application ← Interface ← Infrastructure
  🔵        🟢          🟡           🔴
```

### 2. Interface Segregation ✅
- Application layer defines **interfaces** it needs
- Infrastructure provides **implementations**
- Easy to swap implementations

```python
# Application defines what it needs
class UserRepositoryInterface(ABC):
    async def save(self, user: User) -> User: pass

# Infrastructure provides implementations
class MemoryUserRepository(UserRepositoryInterface): ...
class FileUserRepository(UserRepositoryInterface): ...
```

### 3. Single Responsibility ✅
- **Domain**: Business entities and rules
- **Application**: Use cases and workflows
- **Interface**: Adapters and controllers
- **Infrastructure**: Frameworks and external systems

### 4. Independence ✅
- Business logic works **without** web framework
- Repository can be **swapped** easily
- Each layer is **testable** in isolation

## 🧪 Testing Strategy

### Unit Tests
- **Domain**: Test entities and business rules
- **Application**: Test services with mock repositories
- **Interface**: Test controllers with mock services

### Integration Tests
- Test repository implementations
- Test full request/response flow

### Architecture Tests
- Verify dependency directions
- Ensure layer isolation

## 🚀 Running the Example

### Option 1: Interactive Demo
```bash
cd app_example
python main.py
# Choose option 1 for demo
```

### Option 2: Web Server
```bash
cd app_example
python main.py server
# Visit http://localhost:8000/docs
```

### Option 3: Run Tests
```bash
cd app_example
python test_architecture.py
```

## 🔧 Try These Experiments

### 1. Swap Repository Implementation
In `main.py`, change:
```python
user_repository = MemoryUserRepository()
```
To:
```python
user_repository = FileUserRepository("users.json")
```

**Result**: API works exactly the same, but data persists to file!

### 2. Add Business Rule
In `domain/entities/user.py`, add:
```python
def validate_password_strength(self, password: str):
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters")
```

**Result**: Business rule enforced across all layers automatically!

### 3. Add New Repository
Create `DatabaseUserRepository` implementing `UserRepositoryInterface`:
```python
class DatabaseUserRepository(UserRepositoryInterface):
    # Implement all interface methods
    pass
```

**Result**: Can switch to database without changing any business logic!

## 🎓 Learning Outcomes

After exploring this example, you should understand:

1. **Why** Clean Architecture separates concerns
2. **How** dependency inversion enables flexibility
3. **What** each layer is responsible for
4. **How** to test each layer independently
5. **How** to add features following the patterns

## 🔗 Real-World Applications

This pattern scales to:
- **Microservices** - Each service follows Clean Architecture
- **Large Applications** - Clear boundaries between components
- **Team Development** - Teams can work on different layers
- **Legacy Migration** - Gradually extract business logic

The key is **consistent application** of the dependency rule and clear **separation of concerns**!
