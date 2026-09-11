## Context

Greenfield project implementing an automated code improvement pipeline using self-hosted tools (Ollama, n8n, Flask, ChromaDB). See proposal.md for motivation. The system must orchestrate a multi-iteration loop where an Audit Agent reviews code and a Coding Agent regenerates it, with RAG context from previous iterations stored in ChromaDB.

## Goals / Non-Goals

**Goals:**
- Modular Python codebase with clear separation: config, Flask API, RAG module, agent prompts, n8n workflow
- All configuration centralized in a single config file (YAML)
- Flask API server runs as detached background process launched by n8n via SSH
- n8n workflow drives the entire pipeline including iteration loop, RAG retrieval, agent invocation, and record management
- Qwen2.5-Coder-14B used for both Audit and Coding agents via Ollama HTTP API
- ChromaDB persistence with nomic-embed-text embeddings for iteration context
- Structured iteration records in markdown with consistent format
- Graceful error handling with descriptive logging (no structlog, standard Python exceptions)
- Hard fail-safe: max 5 iterations forced complete

**Non-Goals:**
- No unit tests, pytest, or test framework
- No pyproject.toml or packaging
- No README, deployment guides, or algorithm documentation
- No structlog or correlation_id infrastructure
- No custom exception hierarchy - use standard Python exceptions
- No line-level code edits - Coding Agent regenerates entire files
- No real-time UI or dashboard

## Decisions

### 1. Project Structure
**Decision:** Flat module structure under project root with config.yaml at root.
**Rationale:** Minimal viable pipeline per scope boundaries. Avoids unnecessary packaging complexity.
**Alternatives considered:** src/ layout with pyproject.toml (rejected - scope excludes packaging)

### 2. Configuration Management
**Decision:** Single config.yaml at project root with all tunable parameters (paths, model names, timeouts, chunk sizes, iteration limits, Ollama/Flask/ChromaDB endpoints).
**Rationale:** "No magic values or hard-coded paths" and "Values should be easily configurable from a centralized config file" from requirements.
**Alternatives considered:** Environment variables only (rejected - less discoverable), multiple config files (rejected - against centralized requirement)

### 3. Flask API Design
**Decision:** Flask server with 5 endpoints: GET /api/prompt, POST /api/ingest, GET /api/context, GET/POST /api/iteration/<task>/<iteration>, GET /api/health. Server binds to 0.0.0.0:5000 by default.
**Rationale:** n8n needs HTTP API for all coordination. "Flask server must only host API routes, not execute functions" - business logic in separate modules imported by routes.
**Alternatives considered:** FastAPI (rejected - Flask specified in requirements), embedding logic in routes (rejected - violates separation)

### 4. RAG Implementation
**Decision:** chromadb Python client with persistent client mode. Chunking: 500 chars segment, 50 chars overlap. Embeddings via Ollama HTTP API to nomic-embed-text. Collection per task name.
**Rationale:** Requirements specify exact chunking parameters and embedding model. ChromaDB persistence path configurable.
**Alternatives considered:** In-memory vector store (rejected - persistence required), LangChain (rejected - excessive dependency)

### 5. Agent Prompt Management
**Decision:** Prompt templates stored as .md files in ./prompts/ directory. n8n reads prompt files, substitutes variables, sends to Ollama via HTTP. Two templates: audit_prompt.md, coding_prompt.md.
**Rationale:** "Prompt must be written to a prompt file (txt/md) that n8n reads" from requirements.
**Alternatives considered:** Inline prompts in n8n (rejected - requirement for prompt files), Python string templates (rejected - n8n needs direct access)

### 6. Iteration Record Format
**Decision:** Markdown files with front-matter style fields: TASK, ITERATION_ID, LOC, DESC, IMPROVEMENTS. Draft records from Audit Agent have empty LOC/DESC.
**Rationale:** Requirements specify exact fields and path structure. Markdown enables human readability and easy parsing.
**Alternatives considered:** JSON (rejected - markdown specified), YAML front-matter (rejected - simpler plain text fields preferred)

### 7. n8n Workflow Architecture
**Decision:** Single n8n workflow JSON with nodes: Read Prompt → SSH Launch Flask → Wait → Verify Ollama → Loop (5 iterations) → RAG Retrieval → Audit Agent → Conditional (Continue/Stop) → Coding Agent → Ingest Record → Loop End → Notify → SSH Stop Flask.
**Rationale:** Requirements specify exact node sequence. n8n handles error triggers for all error types listed.
**Alternatives considered:** Multiple workflows (rejected - single pipeline), Python orchestrator (rejected - n8n required)

### 8. Ollama Integration
**Decision:** Direct HTTP calls to Ollama API (localhost:11434) with model-specific timeouts: 10 min for Audit, 5 min for Coding. Model: qwen2.5-coder:14b for both agents, nomic-embed-text for embeddings.
**Rationale:** Requirements specify exact models, timeouts, and self-hosted Ollama.
**Alternatives considered:** Ollama Python client (rejected - direct HTTP simpler, fewer deps), different models per agent (rejected - requirement says same model)

### 9. Error Handling Strategy
**Decision:** Try/except at each external boundary (file I/O, ChromaDB, Ollama HTTP, Flask). Log errors with traceback using standard logging module. n8n error triggers handle workflow-level failures. Continue gracefully where specified (empty RAG context, missing prompt file).
**Rationale:** Requirements list specific error types and mandate "informative logs and stack trace". Standard exceptions per scope boundaries.
**Alternatives considered:** Custom exception classes (rejected - scope excludes), silent failures (rejected - logging required)

## Risks / Trade-offs

- [Ollama model availability] → Mitigation: Health check endpoint in Flask, n8n Verify Ollama node before loop
- [ChromaDB persistence corruption] → Mitigation: Idempotent ingestion (deduplication), graceful degradation to empty context
- [Flask server startup race condition] → Mitigation: 5-second wait node in n8n, health check polling
- [Iteration record format parsing failures] → Mitigation: Strict format validation on read, fallback to empty fields
- [n8n SSH connection failures] → Mitigation: n8n error triggers, SSH key-based auth, timeout configuration
- [Context window overflow in Audit Agent] → Mitigation: Chunking limits context size, top-k retrieval configurable
- [Coding Agent generates syntactically invalid code] → Mitigation: Audit Agent syntax check is explicit requirement, max iterations fail-safe