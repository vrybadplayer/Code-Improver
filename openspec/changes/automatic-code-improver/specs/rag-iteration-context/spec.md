## Purpose

Provides persistent vector storage for iteration records using ChromaDB with nomic-embed-text embeddings, enabling RAG-based context retrieval across improvement iterations.

## ADDED Requirements

### Requirement: ChromaDB persists iteration records
The system SHALL store iteration records in a ChromaDB instance at a configurable path.

#### Scenario: ChromaDB initialization
- **WHEN** system starts and ChromaDB directory does not exist
- **THEN** system creates the directory and initializes ChromaDB

#### Scenario: ChromaDB persistence across runs
- **WHEN** pipeline restarts for same or new task
- **THEN** previously stored iteration records remain queryable

### Requirement: Text chunking with configurable segment size and overlap
The system SHALL split iteration records into 500-character chunks with 50-character overlap by default, both configurable.

#### Scenario: Default chunking parameters
- **WHEN** chunking runs without explicit configuration
- **THEN** system uses 500-character segments with 50-character overlap

#### Scenario: Custom chunking parameters
- **WHEN** chunking is configured with different segment size or overlap
- **THEN** system uses configured values

### Requirement: Embeddings generated via Ollama nomic-embed-text
The system SHALL generate embeddings using Ollama's nomic-embed-text model via HTTP API.

#### Scenario: Embedding generation success
- **WHEN** text chunks are sent to Ollama embedding endpoint
- **THEN** system receives vector embeddings for each chunk

#### Scenario: Embedding service unavailable
- **WHEN** Ollama embedding endpoint returns error or times out
- **THEN** system logs error and continues gracefully without RAG context

### Requirement: RAG retrieval returns relevant context for audit
The system SHALL query ChromaDB using task name and prompt, returning top-k relevant chunks.

#### Scenario: Retrieval with existing records
- **WHEN** querying ChromaDB with task context
- **THEN** system returns relevant chunks formatted as JSON for Audit Agent

#### Scenario: Retrieval with no records
- **WHEN** querying ChromaDB for new task with no history
- **THEN** system returns empty result without error