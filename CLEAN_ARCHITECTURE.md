## Clean Architecture Overview

This document explains the backend's Clean Architecture structure using only the provided folder and file names (no code inspection). It first introduces Clean Architecture, then gives an intuitive mental model, and finally a detailed layer-by-layer mapping to the current `app/` directory layout.

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

Imagine building a house:

- The "blueprints" (domain models & business rules) define what the house MUST be. They shouldn't care whether workers use brand A or B tools.
- The "workers" (services / use cases) read the blueprints and coordinate tasks.
- The "foreman & entry points" (controllers & routers) translate outside requests (humans asking for rooms) into tasks for the workers.
- The "tools & materials" (databases, Milvus, MongoDB, logging, settings) are replaceable — as long as they provide the expected interfaces.

In this backend:

- `models/` & `schema/` define the shapes of core business concepts (keyframes, agents, requests, responses).
- `service/` contains the application logic doing the actual work (searching, model-related operations) without caring *how* persistence is done.
- `repository/` and `common/repository/` wrap database / vector store specifics (Mongo, Milvus) behind abstractions.
- `controller/` orchestrates use cases – calling services, handling edge coordination.
- `router/` exposes HTTP API entrypoints (FastAPI style) that translate web requests to controller calls.
- `core/` holds cross-cutting concerns (settings, dependency wiring, lifecycle, logging).
- `factory/` centralizes object creation / dependency assembly.
- `agent/` encapsulates agent-specific logic (likely higher-level orchestration or autonomous flows) without leaking infra details outward.

So: A request hits a `router/` endpoint → calls a `controller/` function → invokes a `service/` use case → uses `repository/` abstractions → persists or queries data stores → returns domain / schema objects → response schema returned to client.

---

## 3. Detailed Layer Mapping

Below, folders are mapped to Clean Architecture layers, their roles, and directional dependency expectations.

### 3.1 Domain Layer (Core Business Knowledge)

Folders / Files:
- `models/keyframe.py` — Domain entity (likely a persistence model) capturing intrinsic properties (keyframe ids, grouping, etc.).
- `schema/agent.py`, `schema/interface.py`, `schema/request.py`, `schema/response.py` — Data transfer / boundary schema definitions. They straddle domain & interface boundaries: conceptually *domain shapes* expressed for inbound/outbound API contracts.

Principles:
- Pure data + validation logic (if any) without infrastructure dependencies.
- Should not import repositories, services, controllers, or web frameworks.

### 3.2 Application / Use Case Layer

Folders / Files:
- `service/model_service.py` — Contains use cases around model interaction (e.g., inference, vector operations).
- `service/search_service.py` — Encapsulates search logic (vector similarity, retrieval strategies, etc.).
- `agent/agent.py`, `agent/main_agent.py` — Higher-level coordination logic; treat these as *extended application orchestration* (e.g., an autonomous agent pipeline) built on top of services.

Responsibilities:
- Combine domain models + repository gateways to fulfill a user story or operation.
- Contain business flow, not transport concerns.

Dependencies Allowed:
- Can depend on domain (`models/`, `schema/`) and abstract repository interfaces.
- Should not import `router/` or framework specifics.

### 3.3 Interface Adapters Layer

Folders / Files:
- `controller/agent_controller.py`, `controller/query_controller.py` — Orchestrate requests coming from API routers, invocation of services, formatting of returns.
- `common/repository/base.py` — Base repository abstraction; provides generic contract (CRUD, query patterns) used by application services.
- `repository/mongo.py`, `repository/milvus.py` — Concrete repository adapters implementing persistence & retrieval via MongoDB and Milvus (vector DB) respectively.
- `factory/factory.py` — Central assembly: constructs controllers/services/repositories tying implementations to abstractions (Dependency Injection style).

Responsibilities:
- Translate between external formats (HTTP DTOs) and domain/use-case inputs.
- Provide adapter implementations (DB, vector index) behind abstract contracts.

Dependencies Allowed:
- Can depend inward on domain + service + repository abstractions.
- Should not leak outward dependencies into domain models.

### 3.4 Frameworks & Drivers Layer

Folders / Files:
- `router/agent_api.py`, `router/keyframe_api.py` — HTTP/REST endpoints (likely using FastAPI) that bind URLs/methods to controller calls.
- `core/settings.py` — Central configuration (Pydantic Settings) for env-based parameters (DB URIs, hostnames, index settings, etc.).
- `core/dependencies.py` — FastAPI / DI dependency providers (lifecycle-scoped objects like DB/session/repository injection).
- `core/lifespan.py` — Application startup/shutdown hooks.
- `core/logger.py` — Logging configuration and structured logging utilities.
- `app/main.py` — FastAPI app entrypoint wiring routers, middleware, lifespan.

Drivers (External Systems):
- MongoDB (via `repository/mongo.py`)
- Milvus (via `repository/milvus.py`)
- Possibly model inference (loaded in `service/model_service.py` or `agent` logic).

### 3.5 Cross-Cutting & Supporting

Folders / Files:
- `common/repository/__init__.py` — Namespace packaging for repository abstractions.
- `factory/` — Dependency graph assembly (may also enforce singletons or caching of expensive resources).
- `agent/` — While partly application-layer, could also host long-running workflows (background tasks, autonomous loops) — treat carefully to keep dependency direction inward.

### 3.6 Execution Flow Example

1. HTTP request hits `router/keyframe_api.py` endpoint.
2. Router injects dependencies from `core/dependencies.py` (e.g., a controller instance or repository).
3. `controller/query_controller.py` validates input (maybe using `schema/request.py`) and calls a service.
4. `service/search_service.py` uses repository abstractions (base from `common/repository/base.py`) and concrete implementations (`repository/milvus.py`, `repository/mongo.py`).
5. Repositories interact with external systems using settings from `core/settings.py`.
6. Domain models or response schemas from `schema/response.py` are returned outward.
7. Logging happens centrally via `core/logger.py`.

### 3.7 Dependency Direction Recap

```
 [ Routers / Framework ] --> [ Controllers ] --> [ Services / Agents ] --> [ Domain Models / Schemas ]
                                          \-> [ Repository Interfaces ] <- [ Repository Implementations (DB, Milvus) ]
```

Arrows indicate allowed imports (left depends on right). Anything reversed would violate the dependency rule.

### 3.8 Factory / DI Rationale

`factory/factory.py` centralizes construction so:
- You can swap `repository/milvus.py` with another vector DB by changing only the factory.
- Testing becomes easier: inject in-memory or mock repositories.

### 3.9 Settings & Configuration Strategy

`core/settings.py` decouples environment-specific values from code, enabling:
- Twelve-Factor style configuration.
- Reproducible tests (override env vars).
- Simplified migration scripts (they import and reuse the same settings model).

### 3.10 Migration / Scripts Context

Outside `app/` you have migration scripts (e.g., embedding and keyframe migration) that:
- Import `core.settings` and repository logic.
- Operate as outermost procedural utilities (another ring outside Frameworks layer) — they must not introduce inward dependencies.

### 3.11 Logging & Lifespan

`core/lifespan.py` ensures resources (DB clients, model weights, vector indexes) initialize once and cleanly shut down.
`core/logger.py` standardizes logging format so every layer can log without coupling to a specific logging sink.

### 3.12 Agent Subsystem

The `agent/` directory hints at an orchestration or autonomous reasoning component (e.g., chaining LLM/tool calls). Position it at the Application layer, ensuring it only depends on services, schemas, and repositories (never directly on routers or raw framework objects).

### 3.13 Common Pitfalls to Avoid

- Domain models importing FastAPI or Pydantic settings (leaks outward concerns inward).
- Services reaching directly into `core/settings.py` instead of receiving config via DI (couples implementation; prefer injection from factory/dependencies layer).
- Controllers performing heavy logic (should defer to services).
- Repositories returning framework-specific response objects instead of domain/schemas.

### 3.14 How to Add a New Feature (Guided Path)

Suppose you add "Tag keyframes":
1. Domain: Add `models/tag.py` + schema DTOs.
2. Repository: Implement persistence (`repository/mongo_tag.py`) + abstract base if needed.
3. Service: Add `service/tag_service.py` with use cases (create, list, assign).
4. Controller: Add `controller/tag_controller.py` orchestrating service calls.
5. Router: Add endpoints in `router/tag_api.py`.
6. Factory / dependencies: Wire new service & controller.
7. Settings (if external config needed): Extend `core/settings.py`.

### 3.15 Testing Strategy Alignment

- Unit tests: Domain models & services (mock repositories).
- Integration tests: Repository implementations using test DB / Milvus container.
- API tests: Routers (calling test client) verifying end-to-end wiring.

### 3.16 Swap Example: Changing Vector DB

Current: `repository/milvus.py`
Steps to swap:
1. Create `repository/new_vector_store.py` implementing same interface shape.
2. Adjust `factory/factory.py` to return new implementation.
3. No changes required in services or controllers (if abstractions are respected).

---

## 4. Summary Snapshot Table

| Directory / File | Layer | Purpose |
|------------------|-------|---------|
| `models/` | Domain | Core entities (business objects) |
| `schema/` | Domain / Boundary | Request & response DTOs / interfaces |
| `service/` | Application | Use case orchestration logic |
| `agent/` | Application | Higher-level agent / workflow logic |
| `common/repository/` | Interface Adapter | Base repository abstractions |
| `repository/` | Interface Adapter | Concrete data access (Mongo, Milvus) |
| `controller/` | Interface Adapter | Glue between routers and services |
| `router/` | Framework | HTTP endpoint definitions |
| `core/` | Framework / Cross-Cutting | Config, logging, DI helpers, lifecycle |
| `factory/` | Composition | Object graph wiring / dependency assembly |
| `app/main.py` | Entry Point | Application startup / API assembly |
| `migration/` (outside `app/`) | Outer Script Ring | Data import / maintenance tools |

---

## 5. Key Takeaways

- Inward dependency rule preserves flexibility & testability.
- Services hold business flow; controllers stay thin; repositories isolate infrastructure.
- Configuration, logging, and lifecycle management are isolated in `core/`.
- Factory & dependency modules enable swapping implementations with minimal disruption.
- Maintain purity of inner layers by avoiding direct imports from framework-specific modules.

---

## 6. Suggested Next Improvements

1. Introduce explicit repository interfaces (protocols / ABCs) if not already present for Milvus & Mongo.
2. Add a `tests/` hierarchy mirroring layers (domain, services, api) for clarity.
3. Centralize dependency injection (ensure routers only call controllers, never raw services or repositories directly).
4. Add architecture decision records (`docs/adr/`) capturing major technology choices.
5. Introduce type-checked factory functions to reduce runtime wiring errors.

---

Feel free to extend this document as the system evolves (new integrations, caching layer, event-driven components, etc.).
