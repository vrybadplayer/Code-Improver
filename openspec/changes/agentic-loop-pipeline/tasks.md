## 1. Project Setup

- [ ] 1.1 Create directory structure: `./data/iterations/`, `./vector_store/`, `.src/` and verify directories are created
- [ ] 1.2 Set up Python virtual environment and install required packages (chromadb, ollama, flask, etc.) and verify installation succeeds
- [ ] 1.3 Create centralized configuration file (config.yaml) with paths, model names, timeouts and verify it loads correctly
- [ ] 1.4 Install and configure Ollama with Deekseek-r1 and Qwen2.5-coder models and verify models are available
- [ ] 1.5 Install and set up n8n workflow automation tool and verify it's accessible
- [ ] 1.6 Install and set up ChromaDB vector store and verify it's running

## 2. Core Components Development

- [ ] 2.1 Develop Audit Agent component that reviews iteration records and code for errors (encoding, syntax, logical) and verify it returns appropriate status
- [ ] 2.2 Develop Coding Agent component that generates code based on prompts and saves to `.src/` directory and verify code generation works
- [ ] 2.3 Implement RAG ingestion function that stores iteration records in ChromaDB with 500-character chunks and 50-character overlap and verify storage works
- [ ] 2.4 Implement RAG retrieval function that fetches relevant iteration records from ChromaDB using task name and prompt and verify retrieval works
- [ ] 2.5 Create Flask API endpoints for component communication (Auditor, Coder, RAG) and verify endpoints respond correctly
- [ ] 2.6 Implement iteration record handling (creating drafts, completing records) in `./data/iterations/[task name]/Iteration_[iteration number].md` format and verify file creation

## 3. Workflow Automation

- [ ] 3.1 Design n8n workflow that orchestrates the agentic loop with Audit Agent and Coding Agent components and verify workflow structure
- [ ] 3.2 Implement loop control with stop conditions (Status == COMPLETE or Counter == 5) and verify loop terminates correctly
- [ ] 3.3 Implement counter increment and status updates (IN_PROGRESS, IN_REVIEW, COMPLETE) in iteration records and verify state transitions
- [ ] 3.4 Implement improvement proposal generation by Audit Agent and prompt creation for Coding Agent and verify prompt generation
- [ ] 3.5 Configure n8n to be triggerable via IDE (as per requirement) and verify triggering mechanism

## 4. Error Handling and Logging

- [ ] 4.1 Implement centralized logging system that captures errors with context (component, iteration, task) and verify logging works
- [ ] 4.2 Add error handling for local file errors (file not found, read errors) and verify graceful handling
- [ ] 4.3 Add error handling for ChromaDB errors (unavailable, not launched) and verify graceful handling
- [ ] 4.4 Add error handling for Flask API errors (network, server not launched) and verify graceful handling
- [ ] 4.5 Add error handling for embedding service errors (unavailable, invalid response) and verify graceful handling
- [ ] 4.6 Add error handling for Ollama errors (connection error, not launched, invalid model) and verify graceful handling
- [ ] 4.7 Implement n8n error triggers for workflow error handling and verify error triggers work

## 5. Quality Assurance and Requirements Compliance

- [ ] 5.1 Ensure idempotent operation (no duplicate chunks in vector store) and verify deduplication works
- [ ] 5.2 Implement proper cleanup of temporary files and verify cleanup occurs
- [ ] 5.3 Ensure clear documentation of processing steps in code and verify comments are minimal and purposeful
- [ ] 5.4 Verify efficient resource management (no excessive dependencies, imports, or variables)
- [ ] 5.5 Verify comprehensive error logging with proper formatting and context
- [ ] 5.6 Ensure code follows generation rules: purposeful error messages, good naming, minimal comments (one per function/API), no magic values/hard-coded paths, configurable values from centralized config
- [ ] 5.7 Verify Deekseek-r1 is used for audit and Qwen2.5-coder for code edits
- [ ] 5.8 Verify Ollama HTTP nodes have ~15min timeout
- [ ] 5.9 Verify Flask server only hosts API routes (no function execution)
- [ ] 5.10 Verify controller classes/files handle API requests
- [ ] 5.11 Verify prompt is sent to n8n using IDE
- [ ] 5.12 Verify Flask server is designed to be run using n8n instead of manual setup

## 6. Testing and Validation

- [ ] 6.1 Create simple test code improvement task and verify end-to-end pipeline works
- [ ] 6.2 Test with empty files and verify graceful handling
- [ ] 6.3 Test error scenarios (missing files, service unavailability) and verify system handles them gracefully
- [ ] 6.4 Verify iteration records are stored correctly in `./data/iterations/[task name]/Iteration_[iteration number].md`
- [ ] 6.5 Verify source code is saved to `.src/` directory
- [ ] 6.6 Verify RAG ingestion and retrieval work correctly across iterations
- [ ] 6.7 Verify loop stops appropriately when stop conditions are met
- [ ] 6.8 Verify notification mechanism works when process completes
- [ ] 6.9 Verify Flask server closes properly after completion