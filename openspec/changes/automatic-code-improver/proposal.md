## Why

Low-quality prompts to LLMs often produce subpar code that requires multiple manual refinement cycles. This project automates the iterative improvement process by using a self-hosted pipeline (Ollama + n8n + Flask + ChromaDB) to automatically audit, improve, and validate code across multiple iterations without human intervention. The system stores iteration context in a vector database to enable RAG-based learning across cycles.

## What Changes

- New automated code improvement pipeline with configurable iteration loops (default 5)
- RAG-enabled context retrieval using ChromaDB with nomic-embed-text embeddings
- Flask API server hosting HTTP endpoints for n8n integration
- Two specialized LLM agents (Audit Agent and Coding Agent) using Qwen2.5-Coder-14B
- n8n workflow orchestration with SSH-based Flask server lifecycle management
- Structured iteration records with versioned outputs for traceability
- Graceful error handling and hard fail-safes (max 5 iterations forced complete)

## Capabilities

### New Capabilities

- `code-improvement-pipeline`: Core orchestration of multi-iteration code improvement via n8n workflow, Flask API, and dual LLM agents
- `rag-iteration-context`: ChromaDB-backed vector store for storing and retrieving iteration records with 500-char chunks and 50-char overlap
- `audit-agent`: LLM-based code quality auditor that reviews generated code for syntax, logic, and quality compliance
- `coding-agent`: LLM-based code generator that produces complete file replacements based on audit feedback
- `flask-api-routes`: HTTP API endpoints for n8n to trigger ingestion, retrieve context, and manage iterations
- `iteration-record-management`: Structured markdown iteration records with task name, iteration ID, code, descriptions, and improvements

### Modified Capabilities

- None (greenfield project)

## Impact

- New directories: `./data/iterations/`, `./vector_store/`, `src/`, `./prompts/`
- New files: `./data/prompt.md`
- New Python modules: Flask API server, RAG ingestion/retrieval, agent prompts, configuration
- New n8n workflow JSON for end-to-end automation
- Dependencies: ChromaDB, Ollama (Qwen2.5-Coder-14B, nomic-embed-text), Flask, n8n
- Ollama must be running locally with required models pulled
- n8n must have SSH access to launch Flask server as detached background process