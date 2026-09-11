# DESCRIPTION.md (Audited)

```markdown
# Automatic Code Improver

## Overview

A self-hosted pipeline that takes code produced from a low-quality prompt
and iteratively refines it through automated audit and edit loops. Each
iteration is recorded, embedded, and made retrievable so that later runs
build on earlier context. The system runs entirely on local infrastructure
(Ollama + n8n + ChromaDB + Flask) and requires no cloud services.

## Problem

Users who are not prompt-engineering experts produce code that works but
is unreliable: missing error handling, hard-coded values, no naming
conventions, no tests. Manually re-prompting the AI to fix each defect is
slow and inconsistent. Existing AI harnesses (Claude Code, Cursor, Hermes)
assume the user already knows how to prompt well; they do not fix the
underlying prompt-quality gap.

## Audience

Developers using free or local LLMs through simple chat interfaces, who
want better output without learning advanced prompt engineering.

## Value Proposition

1. **Iteration memory.** The system remembers what was tried and what
   worked, so each loop is smarter than the last instead of starting over.
2. **No prompt expertise required.** The user supplies rough code and a
   rough task description; the pipeline handles the refinement.
3. **Auditable history.** Every iteration is written to disk in a known
   format, so the user can trace exactly what changed and why.
4. **Runs offline.** No API keys, no usage costs, no data leaving the
   machine.

## Non-Goals

This project explicitly does NOT:

- Support languages other than Python in v1.
- Refactor across multiple files or entire repositories.
- Replace a human code reviewer or run CI.
- Provide a web UI, dashboard, or chat interface.
- Guarantee correctness. It improves code quality; the user still reviews.
- Handle prompt injection, adversarial input, or untrusted code execution
  (this is a local, single-user tool).

## Glossary

| Term | Definition |
|------|------------|
| **Task** | A named unit of work, e.g. `add_retry_logic`. Used as the folder name and iteration identifier. |
| **Iteration** | One audit → edit → test cycle. Identified by an incrementing integer. |
| **Iteration Record** | A markdown file capturing one iteration's state, code, and reasoning. |
| **Audit Agent** | The LLM (DeepSeek-R1) that reviews code and decides continue/stop. |
| **Coding Agent** | The LLM (Qwen2.5-coder) that produces new code or diffs. |
| **Test Oracle** | The concrete mechanism that decides whether the current code passes. See Test Oracle section. |
| **Hard Error** | A failure that aborts the pipeline (network down, disk full, model unavailable). |
| **Data Value** | An outcome that flows through the pipeline without aborting (audit verdict, test failure). |
| **Low-quality prompt** | A prompt that does not specify error handling, naming, structure, or tests — typically one or two sentences. |

## System Architecture

Five components, each with one responsibility:

1. **n8n** — orchestrator. Owns the loop, branching, retries, and error
   routing. Never contains business logic.
2. **Flask API** — thin HTTP surface. Declares routes and delegates to
   controllers. Never executes business logic inline.
3. **Controllers** — Python classes in `./controllers/` that implement
   each API operation. Called by Flask route handlers.
4. **Ollama** — hosts DeepSeek-R1 (audit) and Qwen2.5-coder (edit).
5. **ChromaDB** — persistent vector store for iteration records.

Data flow:

```
n8n ──HTTP──> Flask route ──call──> Controller ──HTTP──> Ollama
  │                                      │
  │                                      ├──> ChromaDB (read/write)
  │                                      ├──> ./data/iterations/ (write)
  │                                      └──> ./src/ (write)
  │
  └──Execute Command──> start.sh / stop.sh (Flask lifecycle)
```

**Resolved contradiction:** Flask declares routes only. Controllers hold
logic. The two are separate files; Flask imports controllers and calls
them. There are no "Flask-only" business functions.

**Resolved contradiction:** Flask is started by n8n via a single
`start.sh` script that daemonizes Flask and writes its PID to
`./.flask.pid`. Shutdown uses `stop.sh`, which reads the PID and sends
SIGTERM. No SSH. No manual setup.

**Resolved contradiction:** The LLM never touches the filesystem. The
Coding Agent returns structured JSON (see Data Contracts); the
controller applies the change to disk.

## Tech Stack

| Layer | Choice | Version |
|-------|--------|---------|
| Orchestrator | n8n (self-hosted) | latest stable |
| API | Flask | 3.x |
| LLM runtime | Ollama | latest stable |
| Audit model | DeepSeek-R1 | 7B or 14B |
| Edit model | Qwen2.5-coder | 7B |
| Embeddings | nomic-embed-text | via Ollama |
| Vector store | ChromaDB (persistent) | latest stable |
| Language | Python | 3.11+ |

No additional frameworks. No LangChain. No Pydantic (dataclasses are
sufficient). No FastAPI.

## Configuration

All tunable values live in `./config.yaml`. No magic values in code.

```yaml
paths:
  iterations: "./data/iterations"
  source: "./src"
  vector_store: "./vector_store"
  tests: "./tests"
  logs: "./logs"

chunking:
  size: 500
  overlap: 50

ollama:
  host: "http://localhost:11434"
  audit_model: "deepseek-r1:7b"
  edit_model: "qwen2.5-coder:7b"
  embedding_model: "nomic-embed-text"
  timeout_seconds: 900

loop:
  max_iterations: 20
  max_consecutive_no_progress: 2
  global_timeout_seconds: 14400

limits:
  max_file_size_kb: 100
  max_source_dir_mb: 5
  max_llm_output_kb: 8

logging:
  level: "INFO"
  format: "%(asctime)s | %(levelname)s | %(module)s | %(message)s"
```

## Data Contracts

### Iteration Record (`./data/iterations/[task]/Iteration_[n].md`)

YAML frontmatter is the single source of truth for status.

```markdown
---
task: add_retry_logic
iteration_id: 3
status: IN_PROGRESS | IN_REVIEW | COMPLETE | FAILED
verdict: CONTINUE | STOP
confidence: 0.0-1.0
timestamp: 2026-09-11T12:00:00Z
---

## TASK
<task name>

## ITERATION_ID
<integer>

## IMPROVEMENTS
<bullet list of changes proposed by the Audit Agent this iteration; empty on iteration 1>

## LOC
<fenced code blocks, one per file touched, with file path header>

## DESC
<one paragraph per file: what changed and why>

## TEST_RESULTS
<syntax: PASS|FAIL, lint: PASS|FAIL, tests: PASS|FAIL|SKIPPED, details>
```

### Coding Agent Output (JSON)

The Coding Agent must return exactly this shape:

```json
{
  "files": [
    {
      "path": "src/foo.py",
      "mode": "create" | "patch",
      "content": "<full file content when mode=create>",
      "diff": "<unified diff when mode=patch>"
    }
  ],
  "summary": "<one paragraph>"
}
```

The controller validates this JSON against the schema. If it fails to
parse or the paths escape `./src/`, the iteration is marked FAILED and
the pipeline aborts.

### Audit Agent Output (JSON)

```json
{
  "verdict": "CONTINUE" | "STOP",
  "confidence": 0.0,
  "reasoning": "<paragraph>",
  "improvements": ["<bullet>", "..."]
}
```

## Test Oracle

The pipeline's definition of "the code works" is layered. Every layer
must pass for the loop to stop successfully.

| Layer | Check | Mandatory | Tool |
|-------|-------|-----------|------|
| 1 | Syntax valid | Yes | Python `ast.parse` |
| 2 | Lint clean | Yes | `ruff check ./src` |
| 3 | User tests pass | If `./tests/[task]/` exists | `pytest` |
| 4 | Audit Agent verdict | Yes | DeepSeek-R1 |

**Stop condition:** Layers 1 and 2 pass, Layer 3 passes (or is skipped
when no tests exist), and Audit Agent returns `verdict=STOP` with
`confidence >= 0.8`.

**Continue condition:** Any layer fails OR Audit Agent returns
`verdict=CONTINUE`.

**Abort condition:** `max_iterations` reached, OR
`max_consecutive_no_progress` reached (test results identical for N
iterations), OR `global_timeout_seconds` exceeded.

## Functional Requirements

FR-1. n8n receives a task name, an initial prompt, and a source file
      path via a Webhook node. These three inputs are required.

FR-2. n8n starts Flask via `start.sh`. If Flask is already running
      (PID file exists and process is alive), skip.

FR-3. n8n verifies Ollama is reachable at the configured host. If not,
      abort with a Hard Error.

FR-4. n8n queries ChromaDB for prior iteration records matching the
      task name. If none exist, continue with an empty context.

FR-5. n8n enters the loop. On each iteration:

      a. Controller builds the Audit Agent prompt from: task name,
         current source, prior iteration context, and the last test
         results.
      b. Audit Agent returns JSON. Controller validates the schema.
      c. If `verdict=STOP` and test oracle passes, break.
      d. If `verdict=STOP` but test oracle fails, override to CONTINUE
         and log a warning.
      e. Controller writes a draft iteration record with status
         IN_PROGRESS.
      f. Controller builds the Coding Agent prompt from the Audit
         Agent's `improvements`.
      g. Coding Agent returns JSON. Controller validates and applies
         changes to `./src/`.
      h. Controller runs the test oracle. Updates the iteration record
         with LOC, DESC, and TEST_RESULTS. Sets status to IN_REVIEW or
         FAILED.
      i. Controller ingests the completed iteration record into
         ChromaDB (idempotent).

FR-6. When the loop exits, n8n sends a desktop notification with the
      final status and the path to the last iteration record.

FR-7. n8n calls `stop.sh` to shut down Flask.

FR-8. The controller creates `./data/iterations/[task]/`,
      `./src/`, `./vector_store/`, `./logs/`, and `./tests/` if they do
      not exist.

FR-9. Every controller method logs entry, exit, and any exception with
      stack trace to `./logs/pipeline.log`.

FR-10. ChromaDB ingestion uses `sha256(content + iteration_path)` as the
       chunk ID. Before insert, query for existing ID; skip if present.

## Error Taxonomy

**Hard Errors (trigger n8n Error Trigger, abort pipeline):**
- Flask unreachable or returns 5xx
- Ollama unreachable or model not loaded
- ChromaDB unreachable
- File write failure
- Controller returns `{"ok": false, ...}`

**Data Values (flow through pipeline normally):**
- Audit Agent returns `verdict=CONTINUE`
- Test oracle returns FAIL
- No prior iteration records found
- Coding Agent returns zero file changes

The distinction matters: n8n's Error Trigger node fires on Hard Errors
only. Everything else is branching logic.

## Edge Cases

| Case | Resolution |
|------|------------|
| Empty `./src/` | Create a minimal stub from the user's prompt; log INFO. |
| Empty iteration record | Skip ingestion; log WARNING; continue. |
| Ollama timeout | Retry once with same prompt; on second failure, Hard Error. |
| Missing embedding service | Fall back to keyword search over iteration records; log WARNING. |
| Duplicate chunk IDs | Skip insert; log DEBUG. |
| Source file > `max_file_size_kb` | Reject edit; log ERROR; mark iteration FAILED. |
| Context window overflow | Summarize iterations older than 3 into a single "history summary" chunk before sending to Audit Agent. |
| Network interruption mid-loop | Hard Error; preserve current iteration record for manual resume. |
| Incorrect directory path in config | Validate all paths at startup; Hard Error before loop begins. |
| User interrupts pipeline | `stop.sh` terminates Flask; in-progress iteration record remains at IN_PROGRESS status. |
| Two rapid selections / duplicate runs | n8n execution ID is written into the iteration record; duplicates are ignored. |
| Test suite exists but imports fail | Treat as Layer 3 FAIL; continue looping. |
| Coding Agent returns invalid JSON | Retry once; on second failure, Hard Error. |
| Coding Agent patch does not apply | Reject patch; log ERROR; mark iteration FAILED; abort. |

## Milestones

**v1 — Core Loop (build this first)**
- n8n orchestration with a single task
- Flask + controllers
- Ollama integration for both models
- Test oracle layers 1–2 (syntax + lint)
- Iteration record write + read
- In-memory context only (no ChromaDB)

**v2 — Memory**
- ChromaDB persistent store
- Chunking + embeddings
- RAG retrieval in the Audit prompt
- Idempotent ingestion

**v3 — Robustness**
- User-supplied test suite support (Layer 3)
- History summarization for context overflow
- Resume-from-failed-iteration support

Each milestone must be independently runnable. Do not start v2 until v1
completes end-to-end on a trivial task.

## Debugging

- **Flask:** `curl http://localhost:5000/health` must return `{"ok": true}`.
- **Ollama:** `curl http://localhost:11434/api/tags` must list both models.
- **ChromaDB:** `python -c "import chromadb; chromadb.PersistentClient('./vector_store')"` must not raise.
- **n8n:** enable "Save successful executions"; inspect each node's
  input/output payloads.
- **Controllers:** run `pytest ./tests/unit` to verify each controller
  method in isolation.
- **Logs:** `tail -f ./logs/pipeline.log` during a run.

## Verification Checklist

Before declaring the pipeline complete, confirm:

- [ ] `start.sh` launches Flask and writes a valid PID.
- [ ] `stop.sh` terminates Flask cleanly.
- [ ] A trivial task (`add_docstring`) completes in ≤ 3 iterations.
- [ ] Each iteration writes a well-formed record to disk.
- [ ] The test oracle correctly fails invalid syntax.
- [ ] The test oracle correctly fails lint violations.
- [ ] The Audit Agent can return both CONTINUE and STOP verdicts.
- [ ] The Coding Agent can produce both `create` and `patch` modes.
- [ ] ChromaDB ingestion is idempotent across repeated runs.
- [ ] The final notification fires only on successful completion.
- [ ] All Hard Errors trigger the n8n Error Trigger.
- [ ] No path in `config.yaml` is hard-coded anywhere else.

## Code Generation Rules (for the agent building this)

- Think like the laziest senior dev in the room. No unnecessary code.
- Every error message must say what failed, why, and what to do next.
- No features beyond the current milestone.
- Names are descriptive. No abbreviations a new reader cannot decode.
- One comment per function, maximum. No inline narration.
- No magic values. Everything tunable lives in `config.yaml`.
- Every external call is wrapped in try/except with typed error handling.
- Every controller method returns a consistent `{"ok": bool, ...}` shape.
- Every file I/O operation checks existence first and creates if needed.

## Decisions Log

Interpretations made during this audit, recorded for visibility:

1. **Flask vs controllers** was ambiguous. Resolved as: Flask declares
   routes, controllers hold logic. Both exist.
2. **n8n starting Flask via SSH** was marked uncertain in the original.
   Resolved as: local `start.sh` / `stop.sh` scripts, no SSH.
3. **"LLM creates files"** was factually wrong. Resolved as: LLM
   returns JSON, controller writes files.
4. **"LLM tests the result"** was undefined. Resolved as: a layered
   test oracle (syntax → lint → tests → audit verdict).
5. **Status storage location** was unspecified. Resolved as: YAML
   frontmatter in the iteration record file.
6. **Error trigger semantics** were conflated with data values.
   Resolved via the Error Taxonomy section.
7. **Idempotency mechanism** was unspecified. Resolved as: sha256
   chunk IDs checked before insert.
8. **Context overflow** was listed but unsolved. Resolved as: older
   iterations summarized before audit.
9. **Scope** was too large for a single build. Resolved via milestones.
10. **Success metric** was missing. Resolved as: all four test oracle
    layers passing.
```

---

## What I changed, at a glance

**Structural:**
- Split fuzzy "Overview / Purpose / Conclusion" into **Overview, Problem, Audience, Value Proposition, Non-Goals**.
- Added **Glossary**, **Data Contracts**, **Test Oracle**, **Error Taxonomy**, **Milestones**, **Debugging**, **Verification Checklist**, **Decisions Log**.
- Rewrote Value Proposition from component descriptions into user benefits.

**Contradictions resolved:**
- Flask hosts routes, controllers host logic — both exist with a clean boundary.
- Flask lifecycle is `start.sh` / `stop.sh`, not SSH.
- LLM emits JSON, controller writes disk. No file-tool fantasy.
- "LLM tests" became a 4-layer oracle with explicit pass/fail.

**New load-bearing decisions:**
- Status lives in YAML frontmatter of the iteration record — single source of truth.
- Hard Errors vs Data Values are separated. n8n Error Trigger fires on the former only.
- Abort conditions: max iterations, consecutive-no-progress, global timeout.
- Resource limits block runaway LLM output and file writes.
- Idempotency via content-hash chunk IDs.
- Context overflow handled by summarizing old iterations.

**Scope:**
- Cut into three milestones. v1 is ChromaDB-free so the core loop ships first.
- Non-Goals section added as a fence against scope creep.

**Copy:**
- Fixed "Deekseek-r1", "ouptut", "fucntions".
- Deleted the boilerplate Conclusion (which described a different project).

Push back on any of the "Decisions Log" items if my interpretation doesn't match your intent — those ten are the assumptions the coding agent will now treat as ground truth.