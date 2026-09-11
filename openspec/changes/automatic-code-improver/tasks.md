## 1. Project Setup & Configuration

- [ ] 1.1 Create config.yaml at project root with all tunable parameters (paths, model names, timeouts, chunk sizes, iteration limits, Ollama/Flask/ChromaDB endpoints) and verify file is readable by Python
- [ ] 1.2 Create project directory structure: ./data/prompt.md, ./data/iterations/, ./vector_store/, .src/, ./prompts/, and verify directories exist
- [ ] 1.3 Create empty prompt file at ./data/prompt.md and verify it's readable

## 2. Configuration Module

- [ ] 2.1 Implement config.py to load and validate config.yaml with Pydantic or dataclasses, verify it loads without errors
- [ ] 2.2 Add config accessor functions for all settings (paths, models, timeouts, chunk params, endpoints), verify each returns correct type

## 3. Flask API Server

- [ ] 3.1 Implement api_trigger.py with Flask app factory, 5 endpoints (GET /api/prompt, POST /api/ingest, GET /api/context, GET/POST /api/iteration/<task>/<iteration>, GET /api/health), verify server starts on 0.0.0.0:5000
- [ ] 3.2 Implement prompt reading endpoint (GET /api/prompt) that reads ./data/prompt.md, returns 404 if missing, verify with curl
- [ ] 3.3 Implement RAG ingestion endpoint (POST /api/ingest) that accepts iteration record path, chunks content, generates embeddings via Ollama, stores in ChromaDB with deduplication, verify ingestion works
- [ ] 3.4 Implement RAG context retrieval endpoint (GET /api/context) that queries ChromaDB with task name and prompt, returns top-k chunks as JSON, verify returns empty array for new tasks
- [ ] 3.5 Implement iteration record endpoints (GET/POST /api/iteration/<task>/<iteration>) for reading/writing markdown records to ./data/iterations/, verify CRUD operations
- [ ] 3.6 Add health check endpoint (GET /api/health) that verifies Ollama and ChromaDB connectivity, verify returns healthy status

## 4. RAG Module

- [ ] 4.1 Implement rag.py with ChromaDB persistent client initialization, verify client connects to ./vector_store/
- [ ] 4.2 Implement text chunking function (500 chars segment, 50 chars overlap, configurable), verify chunking produces correct segments
- [ ] 4.3 Implement embedding generation via Ollama HTTP API to nomic-embed-text, verify embeddings returned for sample text
- [ ] 4.4 Implement ingestion function that chunks record, generates embeddings, stores in task-named collection with deduplication, verify no duplicates on re-ingest
- [ ] 4.5 Implement retrieval function that queries collection by task name and prompt text, returns top-k chunks as JSON, verify retrieval returns relevant results

## 5. Agent Prompts

- [ ] 5.1 Create ./prompts/audit_prompt.md with template for Audit Agent: receives code, iteration context, quality requirements, outputs Status (IN_PROGRESS/IN_REVIEW/COMPLETE), improvements, and draft iteration record, verify template renders correctly
- [ ] 5.2 Create ./prompts/coding_prompt.md with template for Coding Agent: receives Audit Agent feedback, requirements, context, outputs complete file content, verify template renders correctly
- [ ] 5.3 Create prompt loader utility that reads prompt files and substitutes variables, verify substitution works for both templates

## 6. Ollama Client Module

- [ ] 6.1 Implement ollama_client.py with HTTP calls to Ollama API (localhost:11434), configurable timeouts (10 min audit, 5 min coding), verify connection to running Ollama
- [ ] 6.2 Implement generate_completion() for Audit Agent (qwen2.5-coder:14b, 10-min timeout), verify returns response
- [ ] 6.3 Implement generate_completion() for Coding Agent (qwen2.5-coder:14b, 5-min timeout), verify returns response
- [ ] 6.4 Implement generate_embeddings() for nomic-embed-text, verify returns vector list
- [ ] 6.5 Add error handling for connection errors, timeouts, invalid models, verify graceful degradation

## 7. Iteration Record Management

- [ ] 7.1 Implement iteration_record.py with functions to create draft record (from Audit Agent), complete record (from Coding Agent), read record, verify markdown format matches spec
- [ ] 7.2 Implement record path resolution: ./data/iterations/[task]/Iteration_[n].md with directory creation, verify directories created for new tasks
- [ ] 7.3 Implement record parsing for RAG ingestion (extract text content), verify parsing handles empty LOC/DESC fields

## 8. n8n Workflow

- [ ] 8.1 Create n8n workflow JSON with all 13 nodes per design: Read Prompt → SSH Launch Flask → Wait → Verify Ollama → Loop (5 iterations) → RAG Retrieval → Audit Agent → Conditional → Coding Agent → Ingest Record → Loop End → Notify → SSH Stop Flask
- [ ] 8.2 Configure SSH nodes for Flask launch/stop with detached background process, verify SSH connection works
- [ ] 8.3 Configure Ollama HTTP nodes with correct timeouts (10 min audit, 5 min coding), verify requests succeed
- [ ] 8.4 Configure Flask API HTTP nodes for all 5 endpoints, verify each node works
- [ ] 8.5 Configure error triggers for all error types (file, ChromaDB, Flask, embedding, Ollama), verify error handling works
- [ ] 8.6 Add wait node (5 seconds) after Flask launch, verify Flask is ready before proceeding
- [ ] 8.7 Configure loop with array [1,2,3,4,5] and conditional logic for Audit Agent Status, verify loop executes correctly

## 9. Integration & End-to-End Verification

- [ ] 9.1 Start Ollama with required models (qwen2.5-coder:14b, nomic-embed-text), verify models available
- [ ] 9.2 Launch Flask server via n8n SSH node (or manually for testing), verify health endpoint responds
- [ ] 9.3 Run n8n workflow with a test prompt in ./data/prompt.md, verify pipeline executes
- [ ] 9.4 Verify iteration records created at ./data/iterations/[task]/Iteration_[n].md with correct format
- [ ] 9.5 Verify generated code saved to .src/ directory
- [ ] 9.6 Verify RAG ingestion stores records in ChromaDB, retrieval returns context on subsequent iterations
- [ ] 9.7 Verify hard fail-safe: pipeline stops at iteration 5 with COMPLETE status
- [ ] 9.8 Verify Flask server stops via SSH node on completion
- [ ] 9.9 Verify error scenarios: missing prompt file, Ollama down, ChromaDB unavailable, network timeout - all log errors gracefully