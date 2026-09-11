## Context

See proposal.md - Why. This is a greenfield project implementing an automated code improvement pipeline using self-hosted tools (Ollama, n8n, ChromaDB, Flask). The pipeline transforms low-quality code into production-standard code through iterative audit-code-improve loops with RAG-powered context retrieval.

Key constraints from specs:
- 6 capabilities: agentic-loop-pipeline, iteration-record-management, rag-context-retrieval, dual-agent-audit-code, n8n-workflow-automation, flask-api-server, error-resilience-logging
- Ollama models: DeepSeek-R1 (audit), Qwen2.5-Coder (code), nomic-embed-text (embeddings)
- ~15 minute HTTP timeouts for Ollama calls
- Flask server managed by n8n via SSH, hosts only API routes with controller classes
- ChromaDB at ./vector_store/, iteration records at ./data/iterations/[task]/Iteration_[n].md
- 500-char chunks with 50-char overlap for embeddings
- Max 5 iterations per task
- n8n error triggers for all external service calls

## Goals / Non-Goals

**Goals:**
- Modular, maintainable architecture with clear separation of concerns
- Configuration-driven (no hardcoded paths, models, timeouts)
- Graceful error handling with structured logging for all external dependencies
- Idempotent RAG ingestion to prevent duplicate vectors
- Line-level code modifications (not full file replacement)
- n8n-orchestrated workflow with proper error triggers
- Flask API with controller-based architecture
- Comprehensive test coverage for core processing functions

**Non-Goals:**
- Building a generic RAG framework (purpose-built for iteration records)
- Supporting multiple vector databases (ChromaDB only)
- Supporting multiple embedding models (nomic-embed-text only)
- Building a web UI (n8n + IDE integration only)
- Multi-tenancy or authentication (single-user, local deployment)
- Real-time streaming responses (batch-oriented pipeline)

## Decisions

### 1. Project Structure: Monorepo with capability-based modules
**Decision**: Organize code by capability (pipeline, records, rag, agents, api, errors) rather than layer (controllers, services, models).
**Rationale**: Matches the spec-driven capability boundaries; each capability can be developed/tested independently; aligns with OpenSpec structure.
**Alternatives**: Layered architecture (controllers/services/repositories) - rejected as it scatters related capability logic across directories.

### 2. Configuration: Single YAML file with environment variable overrides
**Decision**: config.yaml at project root with all external service endpoints, paths, timeouts, model names; env vars override for deployment flexibility.
**Rationale**: Centralized config per requirements; YAML readable; env var override standard for containerized deployment.
**Alternatives**: Multiple config files per service - rejected as it fragments configuration; JSON - rejected as less readable for comments.

### 3. Flask API: Blueprint-based controllers with dependency injection
**Decision**: Each capability (ingest, query, health) gets a Blueprint with a Controller class; services injected at app factory creation.
**Rationale**: Controller classes required by spec; Blueprints provide modular routing; DI enables testing with mocks.
**Alternatives**: Class-based views (Flask-Classful) - rejected as adds dependency; route functions with global services - rejected as hard to test.

### 4. ChromaDB Access: Service layer with singleton client
**Decision**: ChromaDBService class manages persistent client; instantiated once per Flask app lifecycle; provides ingest/query/health methods.
**Rationale**: ChromaDB client is thread-safe for reads; singleton avoids connection overhead; service layer isolates DB logic from controllers.
**Alternatives**: Direct client in controllers - rejected as couples controllers to DB; connection per request - rejected as inefficient.

### 5. Ollama Integration: Async HTTP client with retry and timeout
**Decision**: OllamaClient class using httpx.AsyncClient with configurable timeout (~15 min), exponential backoff retry (3 attempts), model validation.
**Rationale**: Long timeouts required; async for potential concurrent requests; retry handles transient failures; model validation catches config errors early.
**Alternatives**: ollama-python library - rejected as less control over timeouts/retries; synchronous requests - rejected as blocks event loop.

### 6. Text Chunking: Deterministic sliding window algorithm
**Decision**: Pure Python function: split text into 500-char chunks with 50-char overlap; handles edge cases (short text, empty); no external deps.
**Rationale**: Spec-defined parameters; deterministic for idempotency; no ML-based chunking needed for structured iteration records.
**Alternatives**: LangChain text splitters - rejected as heavy dependency for simple requirement; recursive splitting - rejected as over-engineered.

### 7. Iteration Record Format: Structured Markdown with YAML frontmatter
**Decision**: Each record is .md file with YAML frontmatter (task, iteration_id, status) + markdown sections (LOC, DESC, IMPROVEMENTS).
**Rationale**: Human-readable + machine-parseable; frontmatter for metadata; markdown sections for code/descriptions; matches spec format.
**Alternatives**: JSON - rejected as less readable for code blocks; pure markdown with regex parsing - rejected as fragile.

### 8. n8n Workflow: Modular sub-workflows per capability
**Decision**: Main workflow calls sub-workflows: health-check, rag-ingest, rag-query, audit-agent, coding-agent, notification; error triggers on each.
**Rationale**: Separation of concerns; reusable sub-workflows; error triggers per spec; easier debugging.
**Alternatives**: Single monolithic workflow - rejected as hard to maintain/debug; external Python scripts for all logic - rejected as bypasses n8n error handling.

### 9. Error Handling: Structured exception hierarchy with correlation IDs
**Decision**: Base PipelineError with subclasses (FileError, ChromaDBError, OllamaError, FlaskError, EmbeddingError); all carry correlation_id, context dict; logged with structlog.
**Rationale**: Typed exceptions enable targeted handling; correlation IDs trace requests across services; structlog provides structured JSON logs.
**Alternatives**: Generic exceptions with string messages - rejected as loses context; logging only, no exceptions - rejected as can't propagate to n8n triggers.

### 10. Testing: Unit tests for pure functions, integration tests for services
**Decision**: pytest with pytest-asyncio; unit tests for chunking, record parsing, config loading; integration tests for ChromaDB service, Ollama client (with testcontainers or mock server); n8n workflows tested manually.
**Rationale**: Fast feedback for logic; integration tests verify external contracts; n8n testing requires running instance.
**Alternatives**: Full E2E tests only - rejected as slow/flaky; no integration tests - rejected as misses service contract bugs.

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Ollama 15-min timeout causes n8n workflow hangs | n8n HTTP node timeout matched; async client with proper cancellation; health check before loop |
| ChromaDB persistence corruption on crash | WAL mode enabled; graceful shutdown in Flask; n8n stop workflow ensures clean exit |
| Duplicate vectors from re-ingestion | Deterministic chunk IDs (task + iteration + chunk_index); upsert semantics in ChromaDB |
| Line-level edits fail on complex refactors | Coding agent prompt enforces line-range format; fallback to full-file if parse fails |
| n8n SSH Flask management fails on Windows | Document SSH setup; provide PowerShell alternative; health endpoint for verification |
| Embedding model mismatch (dimension changes) | Config validates model name; health check includes embedding dimension test |
| Large iteration records exceed context window | Chunking at ingestion; retrieval returns top-k chunks only; audit prompt summarizes |
| Flask port conflicts in concurrent runs | Configurable port; n8n checks port availability before start; random ephemeral port option |

## Migration Plan

1. **Phase 1 - Foundation**: Create project structure, config.yaml, logging, exception hierarchy, config loader
2. **Phase 2 - Core Services**: ChromaDB service, Ollama client, text chunking, iteration record I/O
3. **Phase 3 - Flask API**: App factory, blueprints, controllers, health/ingest/query endpoints
4. **Phase 4 - Agents**: Audit agent (DeepSeek-R1), Coding agent (Qwen2.5-Coder) with prompt templates
5. **Phase 5 - Pipeline Orchestration**: Main loop logic, iteration management, RAG integration
6. **Phase 6 - n8n Workflows**: Sub-workflows, main workflow, error triggers, SSH Flask management
7. **Phase 7 - Testing & Docs**: Unit/integration tests, chunking algorithm docs, deployment guide

**Rollback**: Each phase is independently deployable; config.yaml feature flags can disable capabilities; n8n workflows versioned separately.

## Open Questions

1. **n8n SSH authentication**: Should we use SSH keys, password, or SSH agent? (Affects Flask lifecycle management)
2. **IDE → n8n trigger mechanism**: Webhook, CLI, or file watcher? (Affects input node design)
3. **Vector store backup strategy**: Periodic export? (Not in current scope but needed for production)
4. **Concurrent task support**: Single task at a time or queue? (Current spec implies sequential)