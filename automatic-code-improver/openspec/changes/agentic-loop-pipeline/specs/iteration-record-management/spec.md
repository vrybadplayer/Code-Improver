## Purpose

Manages persistent storage and retrieval of structured iteration records containing task metadata, generated code, descriptions, and improvements for each audit-code-improve cycle.

## ADDED Requirements

### Requirement: Iteration records stored in hierarchical directory structure
The system SHALL store iteration records at `./data/iterations/[task name]/Iteration_[iteration number].md` with task-specific directories.

#### Scenario: Directory created for new task
- **WHEN** first iteration for a new task name begins
- **THEN** system creates `./data/iterations/[task name]/` directory if it doesn't exist

#### Scenario: Iteration file named with sequential number
- **WHEN** iteration N starts
- **THEN** record file named `Iteration_[N].md` (1-indexed)

### Requirement: Iteration records follow structured markdown format
The system SHALL write iteration records with these sections: TASK, ITERATION_ID, LOC, DESC, IMPROVEMENTS.

#### Scenario: Draft record contains task name, iteration ID, improvements
- **WHEN** audit agent creates draft for continuation
- **THEN** record includes TASK, ITERATION_ID, IMPROVEMENTS; LOC and DESC empty

#### Scenario: Completed record contains all fields
- **WHEN** coding agent finishes or audit agent stops
- **THEN** record includes TASK, ITERATION_ID, LOC (generated code), DESC (code description), IMPROVEMENTS

#### Scenario: Record format is machine-parseable
- **WHEN** any component reads iteration record
- **THEN** structured sections allow reliable parsing of each field

### Requirement: System reads previous iteration records for context
The system SHALL read iteration records from previous iterations to provide context to audit agent.

#### Scenario: Previous records retrieved by task name
- **WHEN** pipeline needs context for task
- **THEN** system reads all `Iteration_*.md` files in task directory

#### Scenario: Empty directory handled gracefully
- **WHEN** task directory exists but has no iteration files
- **THEN** system returns empty context, no error

### Requirement: System handles file I/O errors gracefully
The system SHALL log file errors (not found, read errors, write errors, permission errors) with context and continue or fail explicitly.

#### Scenario: Missing file logged with path
- **WHEN** iteration record file not found
- **THEN** error logged with full path, operation continues with empty data

#### Scenario: Write failure logged and propagated
- **WHEN** cannot write iteration record
- **THEN** error logged with path and reason, operation fails explicitly