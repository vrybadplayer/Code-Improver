## Purpose

Provides RAG-powered context retrieval using ChromaDB vector storage with Ollama embeddings to supply relevant historical iteration context to the audit agent during each improvement cycle.

## ADDED Requirements

### Requirement: ChromaDB vector store persistence
The system SHALL persist vector embeddings in ChromaDB at `./vector_store/` with automatic directory creation.

#### Scenario: Vector store directory created on first use
- **WHEN** first embedding operation occurs
- **THEN** system creates `./vector_store/` directory if it doesn't exist

#### Scenario: ChromaDB client initialized with persistent path
- **WHEN** Flask API server starts
- **THEN** ChromaDB client configured with `./vector_store/` persistence path

### Requirement: Text chunking with configured segment size and overlap
The system SHALL chunk iteration record text into 500-character segments with 50-character overlap for embedding.

#### Scenario: Text split into 500-char chunks with 50-char overlap
- **WHEN** iteration record ingested
- **THEN** text split into segments of 500 chars, each overlapping previous by 50 chars

#### Scenario: Short records handled without error
- **WHEN** record text < 500 characters
- **THEN** single chunk created, no overlap needed

#### Scenario: Empty records handled gracefully
- **WHEN** record text is empty
- **THEN** no chunks created, no error

### Requirement: Embeddings generated via Ollama nomic-embed-text
The system SHALL generate vector embeddings using Ollama's nomic-embed-text model via HTTP API.

#### Scenario: Embedding requested for each chunk
- **WHEN** chunking complete
- **THEN** each chunk sent to Ollama embeddings endpoint

#### Scenario: Embedding service errors logged and propagated
- **WHEN** Ollama embedding endpoint unavailable or returns error
- **THEN** error logged with chunk context, operation fails explicitly

#### Scenario: Ollama HTTP timeout configured (~15 minutes)
- **WHEN** embedding request sent
- **THEN** request timeout set to approximately 15 minutes

### Requirement: Context retrieval by task name and prompt similarity
The system SHALL query ChromaDB for relevant chunks using task name filter and prompt embedding similarity.

#### Scenario: Relevant chunks retrieved for audit agent
- **WHEN** pipeline starts iteration
- **THEN** system embeds current prompt, queries ChromaDB filtered by task name, returns top matching chunks

#### Scenario: No results returns empty context
- **WHEN** ChromaDB has no matching chunks for task
- **THEN** empty context returned, no error

#### Scenario: Retrieval errors logged with context
- **WHEN** ChromaDB query fails
- **THEN** error logged with query parameters, empty context returned

### Requirement: Idempotent ingestion prevents duplicate chunks
The system SHALL ensure re-ingesting the same iteration record does not create duplicate vectors.

#### Scenario: Duplicate ingestion produces no new vectors
- **WHEN** same iteration record ingested twice
- **THEN** vector count unchanged, no duplicate chunks stored

### Requirement: Flask API exposes ChromaDB operations
The system SHALL provide HTTP API endpoints for ChromaDB operations (ingest, query, health check) via controller classes.

#### Scenario: Ingest endpoint accepts chunks and metadata
- **WHEN** POST /api/ingest called with chunks and task name
- **THEN** chunks embedded and stored in ChromaDB with task metadata

#### Scenario: Query endpoint returns relevant chunks
- **WHEN** POST /api/query called with prompt and task name
- **THEN** prompt embedded, ChromaDB queried, matching chunks returned

#### Scenario: Health endpoint reports ChromaDB status
- **WHEN** GET /api/health called
- **THEN** returns ChromaDB connection status and collection info