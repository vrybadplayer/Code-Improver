## Purpose

Orchestrates the complete agentic loop pipeline via n8n workflow automation including input acceptance, service health checks, RAG operations, loop control, error handling with triggers, and user notifications.

## ADDED Requirements

### Requirement: n8n workflow accepts prompt input from IDE
The system SHALL provide an n8n input node that accepts text prompts from the user's IDE.

#### Scenario: Input node receives prompt and task name
- **WHEN** user triggers workflow from IDE with prompt text
- **THEN** n8n captures prompt and task name as workflow parameters

### Requirement: n8n workflow verifies Ollama service health
The system SHALL check Ollama service availability before starting the pipeline.

#### Scenario: Ollama health check passes
- **WHEN** workflow starts
- **THEN** n8n calls Ollama health endpoint, proceeds on success

#### Scenario: Ollama health check fails
- **WHEN** Ollama unavailable
- **THEN** workflow stops, error notification sent, no further execution

### Requirement: n8n workflow manages Flask server lifecycle via SSH
The system SHALL start and stop the Flask API server using SSH commands via n8n.

#### Scenario: Flask server started via SSH before RAG operations
- **WHEN** workflow needs ChromaDB access
- **THEN** n8n executes SSH command to start Flask server, waits for readiness

#### Scenario: Flask server stopped via SSH after completion
- **WHEN** pipeline finishes
- **THEN** n8n executes SSH command to stop Flask server

### Requirement: n8n workflow executes iterative loop with conditional branching
The system SHALL implement the audit-code-improve loop using n8n's conditional logic with stop conditions.

#### Scenario: Loop continues while status IN_PROGRESS and counter < 5
- **WHEN** audit agent returns IN_PROGRESS/IN_REVIEW and counter < 5
- **THEN** n8n increments counter, triggers next iteration

#### Scenario: Loop stops on COMPLETE status
- **WHEN** audit agent returns COMPLETE
- **THEN** n8n exits loop, proceeds to completion notification

#### Scenario: Loop stops at max iterations (5)
- **WHEN** counter reaches 5
- **THEN** n8n forces exit, proceeds to completion

### Requirement: n8n workflow handles errors with error triggers
The system SHALL use n8n error triggers for all external service calls (Ollama, Flask, ChromaDB, file operations).

#### Scenario: Ollama error triggers error workflow
- **WHEN** Ollama request fails
- **THEN** n8n error trigger activates, logs error, notifies user

#### Scenario: Flask API error triggers error workflow
- **WHEN** Flask endpoint returns error
- **THEN** n8n error trigger activates, logs error, attempts retry or notifies

#### Scenario: File operation error triggers error workflow
- **WHEN** file read/write fails
- **THEN** n8n error trigger activates, logs error with path context

### Requirement: n8n workflow sends completion notification
The system SHALL notify user when pipeline completes with final status and output location.

#### Scenario: Success notification with output path
- **WHEN** pipeline completes successfully
- **THEN** n8n sends notification with task name, final iteration, output directory

#### Scenario: Failure notification with error details
- **WHEN** pipeline fails unrecoverably
- **THEN** n8n sends notification with error summary and logs location