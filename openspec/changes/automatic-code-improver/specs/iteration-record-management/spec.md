## Purpose

Manages structured iteration records in markdown format, storing task name, iteration ID, generated code, code descriptions, and improvements for each iteration cycle.

## ADDED Requirements

### Requirement: Iteration records stored in structured markdown format
The system SHALL save each iteration record as a markdown file at ./data/iterations/[task name]/Iteration_[iteration number].md.

#### Scenario: Record file path structure
- **WHEN** iteration N for task "example-task" completes
- **THEN** record saved at ./data/iterations/example-task/Iteration_N.md

#### Scenario: Directory creation for new tasks
- **WHEN** first iteration for a new task begins
- **THEN** system creates ./data/iterations/[task name]/ directory

### Requirement: Iteration record contains required fields
The system SHALL include the following fields in each iteration record: TASK (main task name), ITERATION_ID (iteration number), LOC (codes generated), DESC (code descriptions), IMPROVEMENTS (improvements made this iteration if applicable).

#### Scenario: Complete record fields
- **WHEN** iteration record is finalized
- **THEN** all five fields are present with appropriate content

#### Scenario: Draft record partial fields
- **WHEN** Audit Agent creates draft record
- **THEN** TASK, ITERATION_ID, and IMPROVEMENTS filled; LOC and DESC left empty

### Requirement: Iteration records support RAG ingestion
The system SHALL structure records to enable chunking and embedding for RAG retrieval.

#### Scenario: Record chunking for RAG
- **WHEN** iteration record ingested into ChromaDB
- **THEN** record splits into 500-char chunks with 50-char overlap

### Requirement: Iteration records handle empty files gracefully
The system SHALL create and manage iteration records even when generated code is empty.

#### Scenario: Empty code generation
- **WHEN** Coding Agent produces empty output
- **THEN** LOC field records empty state, DESC explains absence, record still saved