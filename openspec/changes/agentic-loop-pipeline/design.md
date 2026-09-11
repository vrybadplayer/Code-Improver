## Context

See proposal.md - Why for motivation. The current state involves manual code improvement processes. Constraints include:
- Must use self-hosted tools (Ollama local LLMs, n8n)
- Specific models: Deekseek-r1 for audit, Qwen2.5-coder for code edits
- Ollama HTTP nodes require ~15min timeout
- Flask server must only host API routes, not execute functions
- Controller classes/files needed to handle API requests
- Prompt must be sent to n8n using IDE
- Flask server should be run using n8n instead of manual setup
- Must follow code generation rules (purposeful error messages, good naming, minimal comments, no magic values, configurable values, graceful error handling)
- Must handle errors gracefully (local file, ChromaDB, Flask API, embedding service, Ollama errors)
- Should create directories if they don't exist
- Must handle empty files gracefully
- Should log all errors and warnings
- Should not require manual intervention for successful execution
- Should not require any additional setup beyond initial configuration
- n8n must handle error using error triggers

## Goals / Non-Goals

**Goals:**
- Create an automated agentic loop pipeline for code improvement
- Implement RAG to retrieve iteration records and generate embeddings
- Use Audit Agent and Coding Agent in a loop with defined stop conditions
- Store iteration records and source code in specified directories
- Ensure idempotent operation, proper cleanup, clear documentation, efficient resource management, and comprehensive error logging
- Follow all technical requirements and rules from DESCRIPTION.md and proposal

**Non-Goals:**
- Manual code review or intervention during the loop
- Using non-self-hosted LLMs or external APIs for core functionality
- Executing functions in the Flask server (only API routing)
- Changing the core LLMs specified (Deekseek-r1 for audit, Qwen2.5-coder for code edits)
- Implementing features beyond the code improvement loop (e.g., deployment, monitoring)

## Decisions

### Architecture Choice: Modular Components
- **Choice**: Separate components for Audit Agent, Coding Agent, RAG ingestion, n8n workflow, and Flask API
- **Rationale**: Isolation of concerns, easier testing and maintenance, aligns with the agentic loop description
- **Alternatives Considered**: 
  - Monolithic script: Rejected because it would be harder to maintain and test
  - Separate microservices: Rejected due to unnecessary complexity for this scope

### Data Flow: ChromaDB as Vector Store
- **Choice**: Use ChromaDB for storing iteration record embeddings
- **Rationale**: Matches requirements, provides efficient similarity search for RAG
- **Alternatives Considered**: 
  - FAISS: Rejected because ChromaDB is easier to integrate with Python and meets requirements
  - Simple file storage: Rejected because it wouldn't support efficient RAG retrieval

### Loop Control: Counter and Status in Iteration Records
- **Choice**: Store counter and status in each iteration record Markdown file
- **Rationale**: Simple, human-readable, persists state between iterations without external dependencies
- **Alternatives Considered**: 
  - External state store (database): Rejected because it adds complexity when simple file-based state suffices
  - In-memory only: Rejected because it wouldn't survive process restarts

### Error Handling: Centralized Logging with Context
- **Choice**: Implement centralized logging that captures error context (component, iteration, task)
- **Rationale**: Meets requirement for informative logs and stack trace, easy identification of issues
- **Alternatives Considered**: 
  - Basic print statements: Rejected because they lack structure and context
  - External logging service: Rejected because it violates self-hosted requirement

### Configuration: Centralized Config File
- **Choice**: Use a centralized configuration file for paths, timeouts, model names, etc.
- **Rationale**: Meets requirement for easily configurable values, avoids magic values/hard-coded paths
- **Alternatives Considered**: 
  - Environment variables only: Rejected because some values (like paths) are better in a file for versioning
  - Hard-coded values: Rejected because it violates configuration requirements

### n8n Integration: IDE-triggered Workflow
- **Choice**: Design n8n workflow to be triggered via IDE (as per requirement) and handle the entire loop
- **Rationale**: Directly follows the requirement that "Prompt must be sent to n8n using IDE"
- **Alternatives Considered**: 
  - CLI-triggered n8n: Rejected because it doesn't meet the IDE requirement
  - Manual n8n execution: Rejected because it requires manual intervention

## Risks / Trade-offs

- [Risk] Ollama service unavailable or slow → Mitigation: Implement retry logic with exponential backoff, timeout handling, and graceful degradation (continue with available context if possible)
- [Risk] ChromaDB performance degradation with large vector store → Mitigation: Implement chunking strategy (500-char with 50-overlap as specified), consider periodic cleanup of old iterations if needed
- [Risk] Infinite loop if stop conditions not met → Mitigation: Hard maximum iteration limit (e.g., 10) in addition to specified stop conditions
- [Risk] Code generated by Coding Agent introduces new errors → Mitigation: Audit Agent reviews each iteration, loop continues only if quality improves or acceptable
- [Risk] Flask server port conflicts → Mitigation: Allow port configuration, implement retry on alternative ports
- [Risk] n8n workflow execution failures → Mitigation: Use n8n's built-in error triggers, implement alerts/notifications

## Migration Plan

1. Set up development environment with required tools (Ollama, n8n, ChromaDB, Flask)
2. Install required Python packages (chromadb, ollama, flask, etc.)
3. Create directory structure: `./data/iterations/`, `./vector_store/`, `.src/`
4. Configure centralized config file with paths, model names, timeouts
5. Develop Audit Agent and Coding Agent components
6. Develop RAG ingestion and retrieval functions
7. Create Flask API endpoints for component communication
8. Design n8n workflow that orchestrates the loop
9. Test with simple code improvement tasks
10. Deploy to production environment (if applicable)

Since this is a new capability, there is no migration from an existing system.

## Open Questions

- Exact format of iteration record Markdown files (beyond the sections mentioned in DESCRIPTION.md)
- Specific prompt templates for Audit Agent and Coding Agent
- Whether to use a single n8n workflow or multiple interconnected workflows
- How to handle concurrent task execution (if multiple tasks are submitted simultaneously)
- Whether to implement a web interface for monitoring or rely solely on logs and notifications