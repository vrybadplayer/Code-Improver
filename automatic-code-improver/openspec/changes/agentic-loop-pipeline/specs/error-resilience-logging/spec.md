## Purpose

Provides comprehensive error handling and logging for all external dependencies (file I/O, ChromaDB, Flask API, Ollama, embeddings) with contextual error messages, stack traces, and n8n error trigger integration.

## ADDED Requirements

### Requirement: Structured logging with severity levels
The system SHALL implement logging with levels (DEBUG, INFO, WARNING, ERROR, CRITICAL) and consistent formatting including timestamp, component, and context.

#### Scenario: Error logs include stack trace and context
- **WHEN** exception occurs
- **THEN** log entry includes full stack trace, operation context, and relevant parameters

#### Scenario: Log output configurable (file, console, both)
- **WHEN** system starts
- **THEN** logging configured via config file for output destinations

### Requirement: File I/O errors handled with path context
The system SHALL catch and log file not found, read errors, write errors, permission errors with full file paths.

#### Scenario: Missing iteration record logged with path
- **WHEN** iteration record file not found
- **THEN** ERROR log with full path, operation returns empty data gracefully

#### Scenario: Write failure logged and propagated
- **WHEN** cannot write iteration record
- **THEN** ERROR log with path and OS error, exception raised for caller handling

### Requirement: ChromaDB errors handled with operation context
The system SHALL catch ChromaDB connection errors, collection errors, query errors with operation details.

#### Scenario: Connection failure logged with endpoint
- **WHEN** ChromaDB client cannot connect
- **THEN** ERROR log with persistence path, operation fails explicitly

#### Scenario: Query error logged with filter parameters
- **WHEN** ChromaDB query fails
- **THEN** ERROR log with task_name and query embedding info

### Requirement: Flask API errors handled with request context
The system SHALL catch Flask request errors, validation errors, and service errors with request details.

#### Scenario: Invalid request returns 400 with details
- **WHEN** malformed JSON or missing fields
- **THEN** WARNING log with request ID, returns 400 with field errors

#### Scenario: Service error returns 500 with correlation ID
- **WHEN** internal service fails
- **THEN** ERROR log with correlation ID, returns 500 with ID for tracing

### Requirement: Ollama errors handled with model and endpoint context
The system SHALL catch Ollama connection errors, model not found, timeout, and invalid response errors.

#### Scenario: Connection error logged with endpoint and model
- **WHEN** Ollama HTTP request fails
- **THEN** ERROR log with base URL, model name, timeout value

#### Scenario: Model not found logged with available models
- **WHEN** requested model not loaded
- **THEN** ERROR log with requested model, lists available models if accessible

#### Scenario: Timeout error logged with duration
- **WHEN** request exceeds ~15 minute timeout
- **THEN** ERROR log with model, prompt length, timeout setting

### Requirement: Embedding service errors handled with chunk context
The system SHALL catch embedding generation errors with chunk index and content preview.

#### Scenario: Embedding failure logged with chunk info
- **WHEN** Ollama embedding endpoint fails for chunk
- **THEN** ERROR log with chunk index, first 100 chars, error details

### Requirement: n8n error triggers receive structured error data
The system SHALL format errors for n8n error trigger consumption with consistent schema.

#### Scenario: Error trigger payload includes all context
- **WHEN** n8n node fails
- **THEN** error payload includes: component, operation, error_type, message, stack_trace, timestamp, correlation_id

### Requirement: Graceful degradation for non-critical failures
The system SHALL continue operation where possible (e.g., empty RAG context) rather than hard failing.

#### Scenario: Missing vector store returns empty context
- **WHEN** ChromaDB unavailable during query
- **THEN** WARNING log, returns empty chunks, pipeline continues

#### Scenario: Ingestion failure logged but doesn't stop loop
- **WHEN** RAG ingest fails after coding agent
- **THEN** ERROR log, iteration record saved locally, loop continues