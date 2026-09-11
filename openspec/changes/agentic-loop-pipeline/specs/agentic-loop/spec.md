## Purpose
Defines the agentic loop pipeline for automatic code improvement, including the workflow, components (Audit Agent, Coding Agent, RAG ingestion), data flow (iteration records, vector store, source code output), and control mechanisms (stop conditions, error handling).

## ADDED Requirements

### Requirement: Agentic Loop Pipeline
The system SHALL provide an agentic loop pipeline that automatically improves code quality through iterative audits and code edits using self-hosted LLMs and n8n workflow automation.

#### Scenario: Initialize Pipeline
- **WHEN** the pipeline is triggered with a task name and initial prompt
- **THEN** the system initializes ChromaDB, ensures Ollama is running, and starts the Flask server for API endpoints

#### Scenario: RAG Retrieval
- **WHEN** the pipeline needs context for the current iteration
- **THEN** the system uses RAG to retrieve relevant iteration records from ChromaDB using the task name and prompt, reads from `./vector_store/`, continues gracefully if no records are found, retrieves 500-character chunks with 50-character overlap, and generates embeddings using Ollama nomic-embed-text

#### Scenario: Audit Agent Review
- **WHEN** the iteration record and generated code are passed to the Audit Agent
- **THEN** the Audit Agent reviews the iteration records and generated code for potential errors (encoding, syntax, logical), decides whether to continue or stop, and passes the Status

#### Scenario: Audit Agent Decision to Continue
- **WHEN** the Audit Agent decides to continue the loop
- **THEN** the system increments the counter, updates Status to IN_PROGRESS or IN_REVIEW, proposes possible improvements, drafts the iteration record in `./data/iterations/[task name]/Iteration_[iteration number].md` (filling only task name, iteration number, and improvements, leaving code sections empty for the Coding Agent), and creates the prompt for the Coding Agent

#### Scenario: Audit Agent Decision to Stop
- **WHEN** the Audit Agent decides to stop the loop (based on stop condition: Status == COMPLETE or Counter == 5)
- **THEN** the system updates Status to COMPLETE, completes the iteration record in `./data/iterations/[task name]/Iteration_[iteration number].md`, and skips prompt creation and Coding Agent

#### Scenario: Coding Agent Workflow
- **WHEN** the Coding Agent receives the prompt from the Audit Agent
- **THEN** the Coding Agent generates the code based on the prompt, saves the code to the specified output directory (`.src/`), and reads and appends to complete the draft of the iteration record in `./data/iterations/[task name]/Iteration_[iteration number].md`

#### Scenario: RAG Ingestion
- **WHEN** the Coding Agent completes the iteration record
- **THEN** the system performs RAG ingestion of the current iteration record in `./data/iterations/[task name]/Iteration_[iteration number].md` into the vector store

#### Scenario: Loop Control
- **WHEN** the stop conditions are not met after an iteration
- **THEN** the system loops to the next iteration
- **WHEN** the stop conditions are met
- **THEN** the system stops the loop and continues with the rest of the pipeline

#### Scenario: Notification and Cleanup
- **WHEN** the loop is completed
- **THEN** the system notifies the user the process is completed and closes the Flask server

#### Scenario: Error Handling
- **WHEN** any of the following errors occur: local file errors, ChromaDB errors, Flask API errors, embedding service errors, or Ollama errors
- **THEN** the system logs the error with appropriate context and handles it gracefully without breaking the system

#### Scenario: Quality Requirements
- **WHEN** the pipeline is operating
- **THEN** the system ensures idempotent operation (no duplicate chunks), proper cleanup of temporary files, clear documentation of processing steps, efficient resource management, and comprehensive error logging with proper formatting

#### Scenario: Code Generation Rules
- **WHEN** the Coding Agent generates code
- **THEN** the code must contain purposeful error messages and stack trace, must not contain excessive features, must have good naming conventions, avoid abbreviated variable names, keep comments to a minimum (preferably one comment per function/API), avoid magic values or hard-coded paths, and have values easily configurable from a centralized config file

#### Scenario: General Rules
- **WHEN** the pipeline is operating
- **THEN** Deekseek-r1 must be used for audit, Qwen2.5-coder must be used for code edits, Ollama HTTP nodes must have ~15min timeout, Flask server must only host API routes (not execute functions), controller classes or files must be needed to handle API requests, prompt must be sent to n8n using IDE, and Flask server should be ran using n8n instead of manual setup (use SSH?)