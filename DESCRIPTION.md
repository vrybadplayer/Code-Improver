# Automatic Code Improver

## Scope Boundaries (v1)
- No unit tests, no integration test framework, no pytest configuration
- No pyproject.toml, no pip install -e . packaging
- No README.md, no deployment guide, no chunking algorithm docs
- No structlog, no correlation_id infrastructure
- No exception class hierarchy — use standard Python exceptions with descriptive messages
- Minimum viable pipeline: config file, Flask routes, two agent scripts, n8n workflow

## Overview
This small project aims to use self-hosted tools such as Ollama local LLMs and n8n to automate tasks instead of human interruption. The goal is to transform low quality code (produced by low quality prompt) into code of standard through multiple automatic audits.

## Value Proposition
1. **Centralized Knowledge Management**: Packages the contents such as code developed, techniques used, possible improvements, etcetera of every loop into a single vector store.
2. **Error Resilience**: Handles failures gracefully without breaking the system, providing informative logs and stack trace, allows easy identification.
3. **Structured Context Management**: Provides clear code context, specifying which file/line of code was developed, how it works, and which iterations were made.
4. **Quality Assurance**: Automatically audits code for quality, suggesting improvements and fixes, ensuring reliability, efficiency, and maintainability.

## Technical Requirements
- ChromaDB persistence store
- Text chunking with 500-character segments and 50-character overlap
- RAG Vector Store retrieval
- Ollama LLM to output iteration context
- To read previous iteration context store for upcoming loops
- Ollama nomic-embed-text embeddings
- n8n automation
- Flask server running HTTP API endpoints
- n8n to utilize python codes in the project directory
- n8n to trigger the ingestion process
- Ollama LLM to have access to create file for new code
- Ollama LLM to regenerate the entire file each iteration
- Ollama LLM to test the produced results before ending iteration

## Purpose
To transform and level up results produced by bad prompt engineering.

## General Rules
- Qwen2.5-Coder-14B must be used for both audit and code edits
- Ollama HTTP nodes must have timeouts: 10 minutes for Audit Agent, 5 minutes for Coding Agent
- Flask server must only host API routes, not execute functions
- Prompt must be written to a prompt file (txt/md) that n8n reads
- Flask server shall be launched by n8n via SSH node as a detached background process (equivalent to running `py api_trigger.py` in a separate terminal)

## Code Generation Rules
- The AI Agent must think like the laziest senior dev in the room, avoid any unnecessary code
- The code must contain purposeful error messages and stack trace
- The code must not contain excessive features that are not necessary for the task at hand
- The code must have good naming conventions and avoid abbreviated variable names that are not identifiable
- Keep comments to a minimum, preferably only one comment for each function/api
- No magic values or hard-coded paths
- Values should be easily configurable from a centralized config file
- Must handle errors gracefully

## Constraints
- Should create directories if they don't exist
- Must handle empty files gracefully
- Should log all errors and warnings
- Should not require manual intervention for successful execution
- Should not require any additional setup beyond the initial configuration
- n8n must handle error using error triggers

## Inputs
- Prompt file path: `./data/prompt.md`
- Iteration records path: `./data/iterations/`
- ChromaDB path: `./vector_store`

## Outputs
- Iteration records output path: `./data/iterations/[task name]/Iteration_[iteration number].md`
- Each iteration record has:
  - Main task name (TASK)
  - Iteration number (ITERATION_ID)
  - Codes generated (LOC)
  - Code descriptions (DESC)
  - Improvements made this iteration if applicable (IMPROVEMENTS)
- Source code output path: `.src/`

## Proposed n8n Workflow
1. Node to read the prompt file from `./data/prompt.md`
2. SSH node to launch the Flask server as a detached background process
3. Wait node (5 seconds) to allow Flask to boot
4. Verify Ollama is running
5. Loop start: hardcoded 5 iterations (array `[1,2,3,4,5]`)
6. RAG retrieval (inside loop):
   - Read from `./vector_store/`
   - Query using task name and prompt
   - Continue gracefully if no iteration records found
   - Retrieve 500-character chunks with 50-character overlap
   - Generate embeddings using Ollama
   - Pass the embedded text into JSON format to Audit Agent for review
7. Pass iteration records to Audit Agent
   - Reviews the iteration records
   - Reviews the generated code for potential errors, including encoding errors, syntax errors, and logical errors.
   - Audit Agent decides whether to continue or not, passing the Status
   - Only set Status = COMPLETE if ALL of these are true:
     1. The code has no syntax errors (verified by running it)
     2. The code meets all Quality Requirements listed in the task
     3. The last improvement did not change the code's behavior
     4. No new errors were introduced in the last iteration
   - Hard fail-safe: if iteration >= 5, force Status = COMPLETE regardless of LLM output
   - If Audit Agent decides to continue:
      - Increment counter
      - Update Status == IN_PROGRESS / IN_REVIEW
      - Propose possible improvements
      - Draft the iteration record in path `./data/iterations/[task name]/Iteration_[iteration number].md`
         - The draft made by the Audit Agent shall follow a pre-set format
         - Only fill in task name, iteration number, and improvements if applicable
         - Leave code related sections empty for the Coding Agent to fill in
      - Create the prompt for the Coding Agent
   - If Audit Agent decides to stop:
      - Update Status == COMPLETE
      - Complete iteration record in path `./data/iterations/[task name]/Iteration_[iteration number].md`
      - Skip prompt creation and Coding Agent
8. Coding Agent workflow
   - Receive the prompt from the Audit Agent
   - Generate the entire file based on the prompt (not line-level edits)
   - Save the code to the specified output directory
   - Read and append to complete the draft of iteration record in path `./data/iterations/[task name]/Iteration_[iteration number].md`
9. RAG ingest only the iteration record of current iteration in path `./data/iterations/[task name]/Iteration_[iteration number].md`
10. Loop to next iteration if conditions met, else stop condition is met and continue with the rest of the pipeline
11. Node to notify the user the process is completed
12. SSH node to close the Flask server
13. End

## Error Handling
- Local file errors (file not found, read errors, etc.)
- ChromaDB errors (unavailable, not launched, etc.)
- Flask API errors (network, server not launched, etc.)
- Embedding service errors (unavailable, invalid response)
- Ollama errors (connection error, not launched, invalid model, etc.)
- All errors logged with appropriate context

## Quality Requirements
- Idempotent operation (no duplicate chunks)
- Proper cleanup of temporary files
- Clear documentation of processing steps
- Efficient resource management
- Comprehensive error logging with proper formatting
- No excessive functions outside of the requirement
- No excessive dependencies outside of the requirement
- No unnecessary imports or unused variables
- No magic numbers or hard-coded values
- No redundant code
- Only write minimum code required to complete the task

## Edge Cases
- Empty directory
- Connection Timed Out
- Software interruption
- Missing embedding service
- Duplicate identifiers
- Network interruptions during processing
- Large files or documents
- Document length exceeding context window
- Incorrect directory path

## Implementation Notes
The implementation should be modular with:
- Separate functions for each component
- Clear error handling paths
- Configuration for ChromaDB path and embedding service
- Logging system for different severity levels
- Documentation of the chunking algorithm

## Conclusion
This component addresses the need for a reliable, multi-source knowledge ingestion system that can be incrementally updated while maintaining query performance and data integrity.