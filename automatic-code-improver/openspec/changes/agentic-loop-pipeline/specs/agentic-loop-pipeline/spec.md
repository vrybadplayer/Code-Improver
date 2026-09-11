## Purpose

Orchestrates iterative code generation, audit, and improvement cycles using RAG-powered context retrieval to transform low-quality code into production-standard code through automated multi-agent loops.

## ADDED Requirements

### Requirement: Pipeline accepts initial prompt and task name
The system SHALL accept a text prompt and task name as input to initiate the improvement loop.

#### Scenario: Valid input starts pipeline
- **WHEN** user provides a non-empty prompt and task name via n8n input node
- **THEN** pipeline initializes with iteration counter = 1 and status = IN_PROGRESS

#### Scenario: Empty prompt is rejected
- **WHEN** user provides empty or whitespace-only prompt
- **THEN** pipeline returns error and does not start

### Requirement: Pipeline executes iterative audit-code-improve loop
The system SHALL execute a loop where each iteration runs an audit agent review followed by a coding agent implementation until stop condition is met.

#### Scenario: Loop continues while status is IN_PROGRESS and iterations < max
- **WHEN** audit agent returns status IN_PROGRESS or IN_REVIEW and iteration counter < 5
- **THEN** pipeline increments counter, creates iteration record draft, and invokes coding agent

#### Scenario: Loop stops when audit agent returns COMPLETE
- **WHEN** audit agent returns status COMPLETE
- **THEN** pipeline finalizes iteration record, skips coding agent, and proceeds to completion

#### Scenario: Loop stops at maximum iteration limit
- **WHEN** iteration counter reaches 5
- **THEN** pipeline forces status COMPLETE, finalizes record, and stops

### Requirement: Pipeline manages iteration records with structured format
The system SHALL create and maintain iteration records at `./data/iterations/[task name]/Iteration_[iteration number].md` with fields: TASK, ITERATION_ID, LOC, DESC, IMPROVEMENTS.

#### Scenario: Draft record created by audit agent
- **WHEN** audit agent decides to continue (status IN_PROGRESS/IN_REVIEW)
- **THEN** draft record created with TASK, ITERATION_ID, and IMPROVEMENTS filled; LOC and DESC left empty

#### Scenario: Coding agent completes the record
- **WHEN** coding agent generates code and saves to output directory
- **THEN** coding agent reads draft, fills LOC and DESC, saves completed record

#### Scenario: Final record created when audit agent stops
- **WHEN** audit agent returns COMPLETE
- **THEN** final record created with all fields populated

### Requirement: Pipeline integrates RAG context retrieval for audit agent
The system SHALL retrieve relevant historical iteration records from ChromaDB using task name and current prompt before each audit.

#### Scenario: Relevant context retrieved for audit
- **WHEN** pipeline starts an iteration
- **THEN** system queries ChromaDB with task name and prompt, retrieves top chunks (500 chars, 50 overlap), passes to audit agent

#### Scenario: Graceful handling when no records exist
- **WHEN** ChromaDB has no iteration records for task
- **THEN** audit agent proceeds with empty context, no error

### Requirement: Pipeline ingests completed iteration records into RAG
The system SHALL ingest only the current iteration's completed record into ChromaDB after coding agent finishes.

#### Scenario: Current iteration record embedded and stored
- **WHEN** coding agent completes iteration record
- **THEN** system chunks record (500 chars, 50 overlap), generates embeddings via Ollama nomic-embed-text, stores in ChromaDB

#### Scenario: Idempotent ingestion prevents duplicates
- **WHEN** same iteration record ingested multiple times
- **THEN** no duplicate chunks created in vector store

### Requirement: Pipeline notifies user on completion
The system SHALL send a completion notification to the user when the loop terminates.

#### Scenario: Notification sent on successful completion
- **WHEN** pipeline reaches stop condition (COMPLETE or max iterations)
- **THEN** n8n sends notification with final status and output location

### Requirement: Pipeline manages Flask server lifecycle
The system SHALL start the Flask API server before RAG operations and shut it down after pipeline completion.

#### Scenario: Flask server started before first RAG operation
- **WHEN** pipeline begins and needs ChromaDB access
- **THEN** n8n starts Flask server via SSH before first API call

#### Scenario: Flask server stopped after pipeline completes
- **WHEN** pipeline finishes all iterations and notifications
- **THEN** n8n stops Flask server via SSH