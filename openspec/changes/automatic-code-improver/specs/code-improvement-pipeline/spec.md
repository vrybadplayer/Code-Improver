## Purpose

Orchestrates the end-to-end multi-iteration code improvement pipeline, coordinating the n8n workflow, Flask API server lifecycle, and dual LLM agents (Audit and Coding) to automatically refine code through up to 5 iterations.

## ADDED Requirements

### Requirement: Pipeline executes configurable number of iterations
The system SHALL execute a configurable number of improvement iterations (default 5) before forcing completion.

#### Scenario: Default iteration count
- **WHEN** pipeline starts without explicit iteration configuration
- **THEN** system runs exactly 5 iterations unless stopped earlier by Audit Agent

#### Scenario: Custom iteration count
- **WHEN** pipeline is configured with a specific iteration limit
- **THEN** system runs up to that many iterations unless stopped earlier

#### Scenario: Hard fail-safe at max iterations
- **WHEN** iteration count reaches the configured maximum
- **THEN** system forces Status = COMPLETE regardless of Audit Agent output

### Requirement: Pipeline manages Flask server lifecycle via n8n SSH
The system SHALL launch the Flask API server as a detached background process via n8n SSH node and terminate it upon pipeline completion.

#### Scenario: Flask server launches successfully
- **WHEN** n8n executes SSH node to start Flask server
- **THEN** server runs as detached background process accessible on configured port

#### Scenario: Flask server terminates on completion
- **WHEN** pipeline reaches completion (COMPLETE status or max iterations)
- **THEN** n8n executes SSH node to stop the Flask server

### Requirement: Pipeline coordinates Audit and Coding agents sequentially
The system SHALL invoke the Audit Agent first, then conditionally invoke the Coding Agent based on Audit Agent's decision.

#### Scenario: Audit Agent continues to Coding Agent
- **WHEN** Audit Agent returns Status = IN_PROGRESS with improvements
- **THEN** pipeline passes prompt to Coding Agent for code generation

#### Scenario: Audit Agent stops pipeline
- **WHEN** Audit Agent returns Status = COMPLETE
- **THEN** pipeline skips Coding Agent and proceeds to finalization

### Requirement: Pipeline integrates RAG retrieval before each audit
The system SHALL retrieve relevant iteration context from ChromaDB before each Audit Agent invocation.

#### Scenario: RAG retrieval on first iteration
- **WHEN** iteration 1 begins and no prior records exist
- **THEN** system continues gracefully with empty context

#### Scenario: RAG retrieval on subsequent iterations
- **WHEN** iteration N > 1 begins
- **THEN** system queries ChromaDB using task name and prompt, retrieves 500-char chunks with 50-char overlap