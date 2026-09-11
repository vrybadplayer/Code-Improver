## Purpose

Generates complete file replacements based on Audit Agent feedback using Qwen2.5-Coder-14B via Ollama, saves code to output directory, and completes iteration records with generated code and descriptions.

## ADDED Requirements

### Requirement: Coding Agent generates entire file from prompt
The system SHALL produce complete file content (not line-level edits) based on the prompt received from the Audit Agent.

#### Scenario: Full file generation
- **WHEN** Coding Agent receives prompt with requirements and context
- **THEN** Coding Agent outputs complete file content for the target file

### Requirement: Coding Agent saves code to specified output directory
The system SHALL write generated code to the configured output directory (default .src/).

#### Scenario: Code saved to output directory
- **WHEN** Coding Agent completes generation
- **THEN** system writes file to .src/ with appropriate naming

#### Scenario: Output directory creation
- **WHEN** output directory does not exist
- **THEN** system creates directory before writing

### Requirement: Coding Agent completes iteration record
The system SHALL read the draft iteration record created by Audit Agent, fill in code sections (LOC, DESC), and save the completed record.

#### Scenario: Iteration record completion
- **WHEN** Coding Agent finishes code generation
- **THEN** system reads draft, appends generated code and descriptions, saves completed record

### Requirement: Coding Agent uses 5-minute Ollama timeout
The system SHALL configure Ollama HTTP requests for Coding Agent with a 5-minute timeout.

#### Scenario: Coding Agent timeout
- **WHEN** Ollama request exceeds 5 minutes
- **THEN** system logs timeout error and handles gracefully