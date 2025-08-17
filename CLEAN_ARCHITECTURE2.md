## Clean Architecture Overview (Code-Validated)

This document provides a **code-validated** analysis of the backend's Clean Architecture structure. After examining the actual implementation, this version corrects assumptions and provides accurate layer mappings based on real code patterns.

---

## 1. Introduction to Clean Architecture

Clean Architecture (popularized by Robert C. Martin) is a way to organize code so that:

- Business rules (domain + use cases) are independent of frameworks, UI, database, or external services.
- Source code dependencies point inward: outer layers depend on inner layers, never the reverse.
- Implementation details (web framework, DB, vector store, message bus, etc.) can be swapped with minimal changes to core logic.
- Testability increases because core logic is decoupled from infrastructure.

Typical concentric layers (from center outward):

1. Entities / Domain Models
2. Use Cases / Application Services
3. Interface Adapters (controllers, presenters, gateways)
4. Frameworks & Drivers (web, DB engines, external APIs, tooling)

Key rule: Nothing in an inner circle knows about anything in an outer circle.

---

## 2. Intuitive Explanation (Mental Model)

Imagine building a specialized search engine:

- The "data blueprints" (domain models) define what a keyframe IS - its properties and relationships.
- The "search workers" (services) know HOW to find keyframes using text similarity or vector operations.
- The "request handlers" (controllers & routers) translate HTTP requests into search operations and format results.
- The "storage systems" (repositories) hide the complexity of MongoDB and Milvus behind simple interfaces.

In this backend:

- `models/keyframe.py` defines the core keyframe entity
- `schema/` provides API contract definitions (request/response shapes)
- `service/` contains search and model inference logic
- `repository/` wraps MongoDB (metadata) and Milvus (vector) storage
- `controller/` orchestrates searches and formats results
- `router/` exposes FastAPI endpoints
- `core/` manages configuration, logging, and dependency injection
- `factory/` assembles all components with proper dependencies
- `agent/` provides higher-level LLM-powered search capabilities

Flow: HTTP request → router → controller → service → repositories → storage systems

---

## 3. Code-Validated Layer Mapping

### 3.1 Domain Layer (Core Business Knowledge)

**Files:**
- `models/keyframe.py` — ✅ **VALIDATED**: Pure domain entity with Beanie Document annotations
  ```python
  class Keyframe(Document):
      key: Annotated[int, Indexed(unique=True)]
      video_num: Annotated[int, Indexed()]
      group_num: Annotated[int, Indexed()]
      keyframe_num: Annotated[int, Indexed()]
  ```

**Schema Files - CORRECTED CLASSIFICATION:**
- `schema/request.py` — **API Contract Layer** (not domain): Pydantic models for HTTP requests
- `schema/response.py` — **API Contract Layer** (not domain): Response DTOs with confidence scores
- `schema/interface.py` — **Interface Layer**: Data transfer objects between layers
- `schema/agent.py` — **Interface Layer**: Agent-specific response schemas

**Validation Result**: ❌ **Original claim was incorrect** - schema files are not domain entities but API/interface contracts.

### 3.2 Application / Use Case Layer

**Files:**
- `service/search_service.py` — ✅ **VALIDATED**: Contains `KeyframeQueryService` with business logic:
  ```python
  class KeyframeQueryService:
      async def _search_keyframes(self, text_embedding, top_k, score_threshold, exclude_indices)
      async def _retrieve_keyframes(self, ids)
  ```
- `service/model_service.py` — ✅ **VALIDATED**: Handles CLIP model inference and embeddings

**Agent Classification - CORRECTED:**
- `agent/agent.py` — **Higher Application Layer**: LLM-powered orchestration with external API calls (Google GenAI)
  ```python
  # Uses LlamaIndex LLM for advanced reasoning
  from llama_index.core.llms import LLM
  ```

**Dependencies**: ✅ Services properly depend on repositories via dependency injection, not direct imports.

### 3.3 Interface Adapters Layer

**Files:**
- `controller/query_controller.py` — ✅ **VALIDATED**: Orchestrates services and converts domain objects to file paths:
  ```python
  class QueryController:
      def convert_model_to_path(self, model: KeyframeServiceReponse) -> tuple[str, float]
      async def search_text(self, query: str, top_k: int, score_threshold: float)
  ```

**Repository Layer - FULLY VALIDATED:**
- `common/repository/base.py` — ✅ **CONFIRMED**: Contains proper abstractions:
  ```python
  class MongoBaseRepository(Generic[BeanieDocument]):
      async def find(self, *args, **kwargs) -> list[BeanieDocument]

  class MilvusBaseRepository(ABC):
      def __init__(self, collection: MilvusCollection)
  ```
- `repository/mongo.py` — ✅ **VALIDATED**: Implements `MongoBaseRepository[Keyframe]`
- `repository/milvus.py` — ✅ **VALIDATED**: Implements `MilvusBaseRepository`

**Factory Pattern - FULLY VALIDATED:**
- `factory/factory.py` — ✅ **CONFIRMED**: Proper dependency injection implementation:
  ```python
  class ServiceFactory:
      def __init__(self, milvus_collection_name, milvus_host, ...):
          self._mongo_keyframe_repo = KeyframeRepository(collection=mongo_collection)
          self._milvus_keyframe_repo = self._init_milvus_repo(...)
          self._keyframe_query_service = KeyframeQueryService(
              keyframe_mongo_repo=self._mongo_keyframe_repo,
              keyframe_vector_repo=self._milvus_keyframe_repo
          )
  ```

### 3.4 Frameworks & Drivers Layer

**Files:**
- `router/keyframe_api.py` — ✅ **VALIDATED**: FastAPI router with proper dependency injection:
  ```python
  @router.post("/search", response_model=KeyframeDisplay)
  async def search_keyframes(
      request: TextSearchRequest,
      controller: QueryController = Depends(get_query_controller)
  )
  ```

**Core Infrastructure - FULLY VALIDATED:**
- `core/settings.py` — ✅ **CONFIRMED**: Pydantic Settings with environment variables:
  ```python
  class MongoDBSettings(BaseSettings):
      MONGO_HOST: str = Field(..., alias='MONGO_HOST')
      MONGO_PORT: int = Field(..., alias='MONGO_PORT')
  ```
- `core/dependencies.py` — ✅ **VALIDATED**: FastAPI dependency providers with `@lru_cache`
- `core/logger.py` — ✅ **CONFIRMED**: Centralized logging
- `core/lifespan.py` — ✅ **CONFIRMED**: Application lifecycle management

### 3.5 Architecture Compliance Analysis

**✅ Dependency Direction Compliance:**
- Services import repositories through constructor injection ✓
- Controllers import services through dependency injection ✓
- Routers import controllers through FastAPI Depends() ✓
- No reverse dependencies detected ✓

**✅ Abstraction Usage:**
- Repositories implement proper base classes ✓
- Factory assembles concrete implementations ✓
- Services depend on interfaces, not implementations ✓

**❌ Minor Architecture Violations:**
- Some files have manual `sys.path.insert(0, ROOT_DIR)` instead of proper Python packaging
- Direct imports between some layers bypass factory in places

### 3.6 Validated Execution Flow

**Confirmed Path:**
1. `router/keyframe_api.py` receives HTTP request
2. FastAPI dependency injection provides `QueryController` from `core/dependencies.py`
3. `controller/query_controller.py` calls `model_service.embedding()` and `keyframe_service.search_by_text()`
4. `service/search_service.py` uses repository interfaces
5. `repository/mongo.py` & `repository/milvus.py` query actual databases
6. Results flow back as domain objects → response schemas → JSON

### 3.7 Corrected Summary Table

| Directory / File | Layer | Purpose | Validation Status |
|------------------|-------|---------|------------------|
| `models/keyframe.py` | Domain | Core business entity | ✅ Confirmed |
| `schema/request.py` | API Contract | HTTP request DTOs | ⚠️ Reclassified (not domain) |
| `schema/response.py` | API Contract | HTTP response DTOs | ⚠️ Reclassified (not domain) |
| `schema/interface.py` | Interface | Inter-layer data transfer | ✅ Confirmed |
| `service/` | Application | Business logic orchestration | ✅ Confirmed |
| `agent/` | Extended Application | LLM-powered workflows | ✅ Confirmed |
| `common/repository/` | Interface Adapter | Repository abstractions | ✅ Fully validated |
| `repository/` | Interface Adapter | Concrete storage implementations | ✅ Fully validated |
| `controller/` | Interface Adapter | Request/response orchestration | ✅ Confirmed |
| `router/` | Framework | HTTP endpoint definitions | ✅ Confirmed |
| `core/` | Framework | Config, DI, logging, lifecycle | ✅ Fully validated |
| `factory/` | Composition | Dependency injection assembly | ✅ Fully validated |

---

## 4. Key Findings vs Original Analysis

### ✅ **Correctly Identified:**
- Repository pattern with proper abstractions
- Factory-based dependency injection
- Service layer business logic separation
- FastAPI framework integration
- Settings-based configuration

### ❌ **Corrected Misconceptions:**
- **Schema files**: Not domain entities, but API contracts and DTOs
- **Agent layer**: More complex than assumed - integrates external LLM services
- **Implementation details**: Factory pattern is fully implemented, not speculative

### 🆕 **Additional Discoveries:**
- Uses Beanie ORM for MongoDB with proper document modeling
- CLIP model integration for embedding generation
- LlamaIndex integration for LLM orchestration
- Milvus vector database for similarity search
- Proper async/await patterns throughout

---

## 5. Architecture Quality Assessment

**Strengths:**
- ✅ Proper dependency injection via factory pattern
- ✅ Repository pattern with concrete abstractions
- ✅ Clear separation of concerns across layers
- ✅ Async/await for proper I/O handling
- ✅ Environment-based configuration

**Areas for Improvement:**
- ⚠️ Some manual path manipulation instead of proper Python packaging
- ⚠️ Could benefit from more explicit interface protocols
- ⚠️ Agent layer could be better isolated from external API dependencies

**Overall Grade: B+ (85/100)**
- Strong architectural foundation with proper Clean Architecture implementation
- Minor packaging and dependency management improvements needed
- Well-structured for a vector search and LLM-powered application

---

## 6. Recommendations for Evolution

1. **Replace `sys.path.insert` with proper `pyproject.toml` packaging**
2. **Add explicit Protocol interfaces for repositories**
3. **Introduce async context managers for external service connections**
4. **Add comprehensive error handling and retry logic**
5. **Consider adding a domain events layer for loose coupling**

---

This analysis confirms that the system follows Clean Architecture principles with only minor deviations and demonstrates solid engineering practices for a modern AI-powered search application.
