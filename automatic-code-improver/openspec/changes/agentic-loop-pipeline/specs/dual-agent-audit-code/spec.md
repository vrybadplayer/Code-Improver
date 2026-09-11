## Purpose

Implements dual-agent system where DeepSeek-R1 audit agent reviews code for errors and proposes improvements, and Qwen2.5-Coder coding agent implements changes with line-level modifications and tests results.

## ADDED Requirements

### Requirement: Audit agent reviews code for errors and proposes improvements
The system SHALL invoke DeepSeek-R1 via Ollama to audit generated code for syntax errors, logical errors, encoding errors, and propose improvements.

#### Scenario: Audit agent receives iteration records and code
- **WHEN** pipeline invokes audit agent
- **THEN** audit agent receives current iteration record draft, generated code, and RAG context

#### Scenario: Audit agent identifies error types
- **WHEN** audit agent reviews code
- **THEN** checks for syntax errors, logical errors, encoding errors, and code quality issues

#### Scenario: Audit agent returns status and improvements
- **WHEN** audit completes
- **THEN** returns status (IN_PROGRESS, IN_REVIEW, COMPLETE) and list of proposed improvements

#### Scenario: Audit agent uses ~15 minute timeout
- **WHEN** audit request sent to Ollama
- **THEN** HTTP timeout configured to approximately 15 minutes

### Requirement: Coding agent implements improvements with line-level edits
The system SHALL invoke Qwen2.5-Coder via Ollama to generate code changes targeting specific lines rather than replacing entire files.

#### Scenario: Coding agent receives audit improvements prompt
- **WHEN** audit agent proposes improvements
- **THEN** coding agent receives prompt with specific improvements to implement

#### Scenario: Coding agent modifies specific lines
- **WHEN** coding agent generates code
- **THEN** outputs changes as line-level modifications (not full file replacement)

#### Scenario: Coding agent saves code to output directory
- **WHEN** code generated
- **THEN** saves to `./src/` directory with appropriate file structure

#### Scenario: Coding agent tests produced results
- **WHEN** code saved
- **THEN** coding agent runs tests/validation before completing iteration

#### Scenario: Coding agent uses ~15 minute timeout
- **WHEN** coding request sent to Ollama
- **THEN** HTTP timeout configured to approximately 15 minutes

### Requirement: Model assignment enforced (DeepSeek-R1 for audit, Qwen2.5-Coder for code)
The system SHALL route audit requests to DeepSeek-R1 and coding requests to Qwen2.5-Coder exclusively.

#### Scenario: Audit requests routed to DeepSeek-R1
- **WHEN** audit agent invoked
- **THEN** Ollama model parameter set to deepseek-r1

#### Scenario: Coding requests routed to Qwen2.5-Coder
- **WHEN** coding agent invoked
- **THEN** Ollama model parameter set to qwen2.5-coder

### Requirement: Agents handle Ollama connection errors gracefully
The system SHALL log Ollama connection errors, model not found errors, and invalid response errors with context.

#### Scenario: Connection error logged and propagated
- **WHEN** Ollama unavailable
- **THEN** error logged with endpoint and model, operation fails explicitly

#### Scenario: Invalid model error logged
- **WHEN** requested model not loaded in Ollama
- **THEN** error logged with model name, operation fails explicitly