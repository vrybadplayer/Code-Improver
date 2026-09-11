# Automatic Code Improver

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
- flask server running HTTP API endpoints
- n8n to utilize python codes in the project directory
- n8n to trigger the ingestion process
- Ollama LLM to have access to create file for new code
- Ollama LLM to modify specific lines of code instead of replacing entire files
- Ollama LLM to test the produced results before ending iteration

## Purpose
To transform and level up results produced by bad prompt engineering.

## General Rules
- Deekseek-r1 must be used for audit
- Qwen2.5-coder must be used for code edits
- Ollama HTTP nodes must have ~15min timeout
- Flask server must only host API routes, not execute fucntions
- Controller classes or files must be needed to handle API requests
- Prompt must be sent to n8n using IDE
- Flask server should be ran using n8n instead of manual setup (use SSH?)

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
- Iteration records path: `./data/iterations/`
- ChromaDB path: `./vector_store`

## Outputs
- Iteration records ouptut path: `./data/iterations/[task name]/Iteration_[iteration number].md`
- Each iteration record has:
  - Main task name (TASK)
  - Iteration number (ITERATION_ID)
  - Codes generated (LOC)
  - Code descriptions (DESC)
  - Improvements made this iteration if applicable (IMPROVEMENTS)
- Source code output path: `.src/`

## Proposed n8n Workflow
1. Node to accept text as input for LLM prompt
2. Initialize ChromaDB client by running the flask server
3. Ensure Ollama is running
4. Uses RAG to retrieve relevant iteration records from ChromaDB using task name and prompt
   - Read from `./vector_store/`
   - Continue gracefully if no iteration records found
   - Retrieve 500-character chunks with 50-character overlap
   - Generate embeddings using Ollama
   - Pass the embedded text to into JSON format to Audit Agent for review
5. Start of loop, define stop condition (e.g. Status == COMPLETE / Counter == 5), Split ELSE condition
6. Pass iteration records to Audit Agent
   - Reviews the iteration records
   - Reviews the generated code for potential errors, including encoding errors, syntax errors, and logical errors.
   - Audit Agent decides whether to continue or not, passing the Status
   - If Audit Agent decides to continue:
      - Increment counter
      - Update Status == IN_PROGRESS / IN_REVIEW
      - Propose possible improvements
      - Draft the iteration record in path `./data/iterations/[task name]/Iteration_[iteration number].md`
         - The draft made by the Audit Agent shall follow a pre-set format 
         - Only fill in task name, iteration number, and improvments if applicable
         - Leave code related sections empty for the Coding Agent to fill in
      - Create the prompt for the Coding Agent
   - If Audit Agent decides to stop: 
      - Update Status == COMPLETE
      - Complete iteration record in path `./data/iterations/[task name]/Iteration_[iteration number].md`
      - Skip prompt creation and Coding Agent
7. Coding Agent workflow
   - Receive the prompt from the Audit Agent
   - Generate the code based on the prompt
   - Save the code to the specified output directory
   - Read and append to complete the draft of iteration record in path `./data/iterations/[task name]/Iteration_[iteration number].md`
8. RAG ingest only the iteration record of current iteration in path `./data/iterations/[task name]/Iteration_[iteration number].md`
9. Loop to next iteration if conditions met, else stop condition is met and continue with the rest of the pipeline
10. Node to notify the user the process is completed
11. Close Flask server
12. End

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
- Unit tests for each processing function
- Documentation of the chunking algorithm

## Conclusion
This component addresses the need for a reliable, multi-source knowledge ingestion system that can be incrementally updated while maintaining query performance and data integrity.
