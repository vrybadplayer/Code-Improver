## Why

This project aims to automate code improvement by transforming low-quality code (produced by low-quality prompts) into code of standard through multiple automatic audits using self-hosted tools such as Ollama local LLMs and n8n. The goal is to reduce human intervention in the code quality loop.

## What Changes

- Create an agentic loop pipeline that uses Ollama LLMs (Deekseek-r1 for audit, Qwen2.5-coder for code edits)
- Use n8n for workflow automation, ChromaDB for vector storage, and a Flask server for API endpoints
- Implement RAG to retrieve iteration records and generate embeddings using Ollama nomic-embed-text
- Create a loop with Audit Agent and Coding Agent to iteratively improve code based on defined stop conditions
- Store iteration records in `./data/iterations/[task name]/Iteration_[iteration number].md` and source code in `.src/`
- Add error handling for local file errors, ChromaDB errors, Flask API errors, embedding service errors, and Ollama errors
- Ensure idempotent operation, proper cleanup, clear documentation, efficient resource management, and comprehensive error logging

## Capabilities

### New Capabilities

- `agentic-loop`: Defines the agentic loop pipeline for automatic code improvement, including the workflow, components (Audit Agent, Coding Agent, RAG ingestion), data flow (iteration records, vector store, source code output), and control mechanisms (stop conditions, error handling).

### Modified Capabilities

<!-- No existing capabilities to modify -->

## Impact

- Adds new directories: `./data/iterations/`, `./vector_store/`, `.src/`
- Introduces new dependencies: Ollama (with models Deekseek-r1 and Qwen2.5-coder), n8n, ChromaDB, Flask
- Affects the development process by automating code quality improvement through iterative audits and code edits
- Requires configuration for ChromaDB path, embedding service, Ollama HTTP nodes timeout (~15min), and Flask server hosting only API routes
- Impact on code: Must follow code generation rules (purposeful error messages, good naming, minimal comments, no magic values, configurable values, graceful error handling)