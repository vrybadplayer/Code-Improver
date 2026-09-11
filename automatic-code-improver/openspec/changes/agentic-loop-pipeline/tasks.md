## 1. Project Setup & Foundation

- [ ] 1.1 Create project directory structure (src/, tests/, config/, data/, vector_store/) and verify all directories exist
- [ ] 1.2 Create config.yaml with all required settings (ChromaDB path, Ollama endpoint, models, timeouts, Flask port, chunk size/overlap) and verify config loads without error
- [ ] 1.3 Create pyproject.toml with dependencies (flask, chromadb, httpx, pyyaml, structlog, pytest, pytest-asyncio) and verify `pip install -e .` succeeds
- [ ] 1.4 Implement config loader (config.py) with YAML parsing, env var overrides, validation, and verify it loads all settings correctly
- [ ] 1.5 Implement structured logging setup (logging.py) with structlog, severity levels, JSON formatting, file/console output, and verify log output appears correctly
- [ ] 1.6 Implement exception hierarchy (exceptions.py) with PipelineError base and subclasses (FileError, ChromaDBError, OllamaError, FlaskError, EmbeddingError) with correlation_id and context, and verify exceptions can be raised/caught with context preserved

## 2. Core Services

- [ ] 2.1 Implement ChromaDB service (chromadb_service.py) with singleton client, persist directory creation, ingest/query/health methods, and verify it connects to ./vector_store/ and returns collection info
- [ ] 2.2 Implement Ollama client (ollama_client.py) with async httpx, configurable timeout (~15 min), exponential backoff retry (3 attempts), model validation, and verify it calls Ollama health/embeddings/generate endpoints successfully
- [ ] 2.3 Implement text chunking (chunking.py) with deterministic 500-char segments, 50-char overlap, edge case handling (short/empty text), and verify unit tests pass for various input lengths
- [ ] 2.4 Implement iteration record I/O (records.py) with YAML frontmatter + markdown sections, read/write draft/completed records, directory creation, and verify records can be written to ./data/iterations/[task]/Iteration_[n].md and read back correctly
- [ ] 2.5 Implement record parser (record_parser.py) to extract TASK, ITERATION_ID, LOC, DESC, IMPROVEMENTS from markdown files, and verify it correctly parses both draft and completed records

## 3. Flask API Server

- [ ] 3.1 Create Flask app factory (create_app.py) with blueprint registration, dependency injection for services, config loading, and verify app starts and responds to health endpoint
- [ ] 3.2 Implement HealthController (health_controller.py) with GET /api/health returning ChromaDB status, collection info, vector count, and verify it returns healthy/unhealthy JSON correctly
- [ ] 3.3 Implement IngestController (ingest_controller.py) with POST /api/ingest accepting chunks + task_name, calling ChromaDB service, returning result, and verify it stores vectors with task metadata
- [ ] 3.4 Implement QueryController (query_controller.py) with POST /api/query accepting prompt + task_name, embedding prompt, querying ChromaDB, returning chunks, and verify it returns relevant chunks for a test task
- [ ] 3.5 Add request validation, correlation ID middleware, error handlers for 400/500 with structured error responses, and verify invalid requests return 400 with field errors
- [ ] 3.6 Create SSH management scripts (start_flask.sh, stop_flask.sh) for n8n to start/stop Flask server, and verify they launch/terminate the server on configured port

## 4. Agent Implementation

- [ ] 4.1 Create audit agent (audit_agent.py) using DeepSeek-R1 via OllamaClient, prompt template for code review (syntax, logic, encoding errors), returning status + improvements, and verify it returns IN_PROGRESS/COMPLETE with improvements for test code
- [ ] 4.2 Create coding agent (coding_agent.py) using Qwen2.5-Coder via OllamaClient, prompt template for line-level edits, saving to ./src/, running tests, and verify it modifies specific lines and saves files correctly
- [ ] 4.3 Implement agent prompt templates (prompts/) with structured prompts for audit and coding agents, and verify prompts produce expected output format
- [ ] 4.4 Add model routing enforcement (DeepSeek-R1 for audit, Qwen2.5-Coder for code) in agent factory, and verify wrong model cannot be used for an agent type

## 5. Pipeline Orchestration

- [ ] 5.1 Implement main pipeline orchestrator (pipeline.py) with iteration loop, stop conditions (COMPLETE status or max 5 iterations), iteration counter, status management, and verify it runs a full loop with mock agents
- [ ] 5.2 Integrate RAG context retrieval in pipeline: query ChromaDB before audit, pass chunks to audit agent, and verify relevant context is retrieved for a task with existing records
- [ ] 5.3 Integrate RAG ingestion in pipeline: after coding agent completes, chunk record, embed via Ollama, ingest via Flask API, and verify new vectors appear in ChromaDB for the task
- [ ] 5.4 Implement iteration record management in pipeline: create draft from audit, complete from coding agent, finalize on COMPLETE, and verify records are created at correct paths with correct format
- [ ] 5.5 Add graceful error handling in pipeline: catch service errors, log with context, continue where possible (empty RAG context), fail explicitly for critical errors, and verify error logs contain correlation IDs and context

## 6. n8n Workflow Automation

- [ ] 6.1 Create n8n sub-workflow: Health Check (Ollama, Flask) with error triggers, and verify it succeeds when services are healthy and fails with error trigger when not
- [ ] 6.2 Create n8n sub-workflow: RAG Ingest (call Flask /api/ingest) with error trigger, and verify it ingests chunks and returns success
- [ ] 6.3 Create n8n sub-workflow: RAG Query (call Flask /api/query) with error trigger, and verify it returns chunks for a test prompt
- [ ] 6.4 Create n8n sub-workflow: Audit Agent (call audit agent) with error trigger, and verify it returns status and improvements
- [ ] 6.5 Create n8n sub-workflow: Coding Agent (call coding agent) with error trigger, and verify it generates code and saves to ./src/
- [ ] 6.6 Create n8n sub-workflow: Notification (success/failure) with error trigger, and verify it sends notification with correct details
- [ ] 6.7 Create main n8n workflow orchestrating sub-workflows with conditional loop (IF node for status/counter), SSH nodes for Flask start/stop, input node for IDE prompt, and verify full workflow runs end-to-end for a test task
- [ ] 6.8 Configure n8n error triggers on all external service nodes with structured error payload, and verify error workflow activates and logs correctly on simulated failures

## 7. Testing & Documentation

- [ ] 7.1 Write unit tests for chunking.py (various text lengths, edge cases) and verify all pass with `pytest tests/test_chunking.py`
- [ ] 7.2 Write unit tests for records.py and record_parser.py (draft/completed, parsing) and verify all pass
- [ ] 7.3 Write unit tests for config.py (loading, validation, env overrides) and verify all pass
- [ ] 7.4 Write integration tests for ChromaDB service (ingest, query, health) with real ChromaDB and verify all pass
- [ ] 7.5 Write integration tests for Ollama client (health, embeddings, generate) with mock server or real Ollama and verify all pass
- [ ] 7.6 Write integration tests for Flask API (all endpoints) with test client and verify all pass
- [ ] 7.7 Write integration test for full pipeline (mock agents, real services) and verify it completes a test task end-to-end
- [ ] 7.8 Document chunking algorithm (docs/chunking.md) with parameters, examples, idempotency guarantee, and verify documentation is clear
- [ ] 7.9 Create deployment guide (docs/deployment.md) with n8n setup, SSH config, Ollama model pulls, directory permissions, and verify guide enables fresh deployment
- [ ] 7.10 Create README.md with project overview, architecture diagram, quick start, and verify it renders correctly on GitHub