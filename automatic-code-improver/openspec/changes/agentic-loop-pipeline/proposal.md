## Why

This project automates the transformation of low-quality code (produced by poor prompt engineering) into production-standard code through multiple automated audit-iteration loops. It uses self-hosted tools (Ollama LLMs, n8n, ChromaDB) to eliminate human intervention while building a persistent knowledge base of all iterations for continuous improvement.

## What Changes

- **New Capability**: Agentic Loop Pipeline — orchestrates iterative code generation, audit, and improvement cycles using RAG-powered context retrieval
- **New Capability**: Iteration Record Management — stores and retrieves structured iteration records (task name, iteration ID, generated code, descriptions, improvements) with ChromaDB vector storage
- **New Capability**: RAG-Powered Context Retrieval — embeds iteration records using Ollama nomic-embed-text, retrieves relevant context via 500-char chunks with 50-char overlap for audit agent
- **New Capability**: Dual-Agent Audit & Code Generation — DeepSeek-R1 for code audit/review, Qwen2.5-Coder for code edits with line-level modifications
- **New Capability**: n8n Workflow Automation — end-to-end pipeline orchestration including Flask API server lifecycle, Ollama health checks, error triggers, and user notifications
- **New Capability**: Flask API Server — HTTP endpoints for ChromaDB operations, managed by n8n (not manual)
- **New Capability**: Error Resilience & Logging — graceful failure handling with informative logs, stack traces, and n8n error triggers for all external dependencies

## Capabilities

### New Capabilities
- `agentic-loop-pipeline`: Core orchestration of iterative audit-code-improve cycles with configurable stop conditions (status COMPLETE or max iterations)
- `iteration-record-management`: Persistent storage and retrieval of iteration records in `./data/iterations/[task name]/Iteration_[n].md` with structured format
- `rag-context-retrieval`: ChromaDB vector store with Ollama embeddings for retrieving relevant historical context (500-char chunks, 50-char overlap)
- `dual-agent-audit-code`: DeepSeek-R1 audit agent reviews code for syntax/logical/encoding errors and proposes improvements; Qwen2.5-Coder implements changes with line-level edits
- `n8n-workflow-automation`: Complete pipeline orchestration including input acceptance, service health checks, RAG ingestion, loop control, and completion notification
- `flask-api-server`: HTTP API endpoints for ChromaDB operations, controller-based request handling, managed by n8n via SSH
- `error-resilience-logging`: Comprehensive error handling for file I/O, ChromaDB, Flask API, embeddings, Ollama connections with contextual logging

### Modified Capabilities
- None (greenfield project)

## Impact

- **New directories**: `./data/iterations/`, `./vector_store/`, `./src/`
- **New dependencies**: Ollama (DeepSeek-R1, Qwen2.5-Coder, nomic-embed-text), n8n, ChromaDB, Flask
- **Configuration**: Centralized config for ChromaDB path, embedding service, model selection, timeouts (~15min for Ollama HTTP)
- **API surface**: Flask endpoints for ChromaDB operations (controller classes required)
- **n8n workflows**: Must handle error triggers, SSH for Flask server lifecycle, IDE prompt input
- **Testing**: Unit tests for each processing function, chunking algorithm documentation