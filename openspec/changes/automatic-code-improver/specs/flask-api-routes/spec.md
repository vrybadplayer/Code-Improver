## Purpose

Provides HTTP API endpoints for n8n to trigger the improvement pipeline, retrieve RAG context, manage iteration state, and coordinate agent interactions.

## ADDED Requirements

### Requirement: Flask server hosts only API routes
The system SHALL run a Flask server that exclusively hosts HTTP API endpoints without executing business logic directly.

#### Scenario: API-only server
- **WHEN** Flask server starts
- **THEN** server only exposes HTTP routes, all processing delegated to separate modules

### Requirement: Endpoint to read prompt file
The system SHALL provide an API endpoint that reads the prompt file from ./data/prompt.md.

#### Scenario: Prompt file read
- **WHEN** n8n calls GET /api/prompt
- **THEN** system returns prompt content from ./data/prompt.md

#### Scenario: Prompt file not found
- **WHEN** prompt file does not exist
- **THEN** system returns 404 with descriptive error

### Requirement: Endpoint to trigger RAG ingestion
The system SHALL provide an API endpoint that ingests the current iteration record into ChromaDB.

#### Scenario: Ingestion triggered
- **WHEN** n8n calls POST /api/ingest with iteration record path
- **THEN** system chunks record, generates embeddings, stores in ChromaDB

#### Scenario: Ingestion idempotency
- **WHEN** same iteration record ingested multiple times
- **THEN** system avoids duplicate chunks in ChromaDB

### Requirement: Endpoint to retrieve RAG context
The system SHALL provide an API endpoint that queries ChromaDB and returns relevant context for the Audit Agent.

#### Scenario: Context retrieval
- **WHEN** n8n calls GET /api/context with task name and prompt
- **THEN** system returns relevant chunks as JSON

### Requirement: Endpoint to manage iteration state
The system SHALL provide API endpoints to read/write iteration status and records.

#### Scenario: Iteration status read
- **WHEN** n8n calls GET /api/iteration/[task]/[iteration]
- **THEN** system returns iteration record content

#### Scenario: Iteration status write
- **WHEN** n8n calls POST /api/iteration/[task]/[iteration] with record data
- **THEN** system saves record to ./data/iterations/[task]/Iteration_[iteration].md

### Requirement: Flask server launched as detached background process
The system SHALL support being launched via SSH as a detached process (equivalent to `py api_trigger.py &`).

#### Scenario: Detached launch
- **WHEN** n8n SSH node executes launch command
- **THEN** Flask server runs in background, accessible via HTTP