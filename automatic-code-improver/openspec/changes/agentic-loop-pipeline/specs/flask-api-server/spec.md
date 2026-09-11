## Purpose

Provides HTTP API endpoints for ChromaDB operations (ingest, query, health) with controller-based request handling, managed by n8n via SSH for lifecycle control.

## ADDED Requirements

### Requirement: Flask server hosts only API routes, no business logic
The system SHALL run a Flask server that only exposes HTTP endpoints; all business logic resides in controller classes.

#### Scenario: Flask app registers only route handlers
- **WHEN** Flask server starts
- **THEN** routes mapped to controller methods, no inline logic in route definitions

### Requirement: Controller classes handle API requests
The system SHALL implement controller classes for each API domain (ingest, query, health).

#### Scenario: Ingest controller handles chunk storage
- **WHEN** POST /api/ingest received
- **THEN** IngestController validates payload, calls ChromaDB service, returns result

#### Scenario: Query controller handles context retrieval
- **WHEN** POST /api/query received
- **THEN** QueryController validates payload, calls ChromaDB service, returns chunks

#### Scenario: Health controller reports service status
- **WHEN** GET /api/health received
- **THEN** HealthController checks ChromaDB connection, returns status JSON

### Requirement: Ingest endpoint accepts chunks with task metadata
The system SHALL provide POST /api/ingest accepting JSON with chunks array and task_name.

#### Scenario: Valid ingest request stores vectors
- **WHEN** POST /api/ingest with {chunks: [...], task_name: "..."}
- **THEN** each chunk embedded via Ollama, stored in ChromaDB with task_name metadata

#### Scenario: Invalid payload returns 400
- **WHEN** POST /api/ingest missing chunks or task_name
- **THEN** returns 400 with error details

### Requirement: Query endpoint returns relevant chunks
The system SHALL provide POST /api/query accepting JSON with prompt and task_name.

#### Scenario: Valid query returns matching chunks
- **WHEN** POST /api/query with {prompt: "...", task_name: "..."}
- **THEN** prompt embedded, ChromaDB queried with task filter, top chunks returned

#### Scenario: Empty results returns empty array
- **WHEN** no matching chunks found
- **THEN** returns 200 with empty chunks array

### Requirement: Health endpoint reports ChromaDB status
The system SHALL provide GET /api/health returning ChromaDB connection status and collection info.

#### Scenario: Healthy response includes collection count
- **WHEN** ChromaDB connected
- **THEN** returns {status: "healthy", collections: [...], vector_count: N}

#### Scenario: Unhealthy response includes error
- **WHEN** ChromaDB disconnected
- **THEN** returns {status: "unhealthy", error: "..."}

### Requirement: Configuration via centralized config file
The system SHALL read ChromaDB path, Ollama endpoint, and server port from a config file (no hardcoded values).

#### Scenario: Config loaded at startup
- **WHEN** Flask server starts
- **THEN** reads config.yaml for all external service endpoints and paths

### Requirement: Server managed by n8n via SSH
The system SHALL be startable/stoppable via SSH commands for n8n lifecycle management.

#### Scenario: Start command launches server in background
- **WHEN** SSH start command executed
- **THEN** Flask server starts, binds to configured port, ready for requests

#### Scenario: Stop command terminates server gracefully
- **WHEN** SSH stop command executed
- **THEN** Flask server shuts down, releases port