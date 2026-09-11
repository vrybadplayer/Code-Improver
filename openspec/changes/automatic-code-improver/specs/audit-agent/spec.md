## Purpose

Reviews generated code for syntax errors, logical errors, encoding issues, and quality compliance using Qwen2.5-Coder-14B via Ollama, deciding whether to continue improvement iterations or mark as complete.

## ADDED Requirements

### Requirement: Audit Agent reviews code for syntax and logical errors
The system SHALL analyze generated code for syntax errors, encoding errors, and logical errors using the Audit Agent LLM.

#### Scenario: Syntax error detection
- **WHEN** Audit Agent receives code with syntax errors
- **THEN** Audit Agent identifies and reports syntax errors in its review

#### Scenario: Logical error detection
- **WHEN** Audit Agent receives code with logical flaws
- **THEN** Audit Agent identifies and reports logical errors in its review

### Requirement: Audit Agent verifies quality requirements compliance
The system SHALL verify that generated code meets all Quality Requirements specified in the task.

#### Scenario: Quality requirements met
- **WHEN** generated code satisfies all task quality requirements
- **THEN** Audit Agent acknowledges compliance in its review

#### Scenario: Quality requirements not met
- **WHEN** generated code fails one or more quality requirements
- **THEN** Audit Agent identifies specific unmet requirements

### Requirement: Audit Agent decides continuation status
The system SHALL output a Status value of IN_PROGRESS, IN_REVIEW, or COMPLETE based on review findings.

#### Scenario: Continue iteration
- **WHEN** code has errors or unmet requirements and iteration < max
- **THEN** Audit Agent returns Status = IN_PROGRESS with proposed improvements

#### Scenario: Stop iteration - all criteria met
- **WHEN** code has no syntax errors, meets all quality requirements, last improvement did not change behavior, no new errors introduced
- **THEN** Audit Agent returns Status = COMPLETE

#### Scenario: Stop iteration - max iterations reached
- **WHEN** iteration count >= configured maximum (default 5)
- **THEN** Audit Agent returns Status = COMPLETE regardless of other findings

### Requirement: Audit Agent drafts iteration record with improvements
The system SHALL produce a draft iteration record containing task name, iteration number, and proposed improvements, leaving code sections empty for Coding Agent.

#### Scenario: Draft record creation
- **WHEN** Audit Agent returns Status = IN_PROGRESS
- **THEN** system creates draft at ./data/iterations/[task name]/Iteration_[iteration number].md with improvements filled, code sections empty

### Requirement: Audit Agent uses 10-minute Ollama timeout
The system SHALL configure Ollama HTTP requests for Audit Agent with a 10-minute timeout.

#### Scenario: Audit Agent timeout
- **WHEN** Ollama request exceeds 10 minutes
- **THEN** system logs timeout error and handles gracefully