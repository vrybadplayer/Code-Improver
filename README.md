```markdown
# Code-Improver-Hermes

An automated code improvement pipeline that iteratively audits, rewrites, and refines code using self-hosted LLMs, a vector store, and n8n orchestration.

Built as a zero-cost experiment in spec-driven development, local LLM agents, and workflow automation — no cloud APIs, no subscriptions, no paid tools.

---

## What it does

Given a task prompt written to `./data/prompt.md`, the pipeline:

1. Generates an initial version of the code using a local LLM.
2. Runs **n iterations** (default: 5) where:
   - An **Audit Agent** reviews the current code and outputs a numbered list of improvements.
   - A **Coding Agent** rewrites the file applying those improvements.
   - An **Iteration Record** is written to disk and embedded into a vector store.
3. RAG retrieval feeds prior iteration context back into the next audit.
4. The final output lands in `src/<task-name>/output.md`.

Every iteration is persisted, retrievable, and self-referencing.

> **Where to put your prompt:** write your task into `./data/prompt.md` before running the workflow.
>
> **How to change the iteration count:** open the n8n workflow and edit the `For Loop` node. Its `Array.from({ length: 5 }, ...)` line controls how many iterations run. Change `5` to any positive integer.

---

## Stack

| Layer | Tool | Purpose |
| :--- | :--- | :--- |
| Orchestration | [n8n](https://n8n.io) (self-hosted) | Workflow driver, loop control, branching |
| Local LLM | [Ollama](https://ollama.com) | Code generation + audit reasoning |
| Coding model | `qwen2.5-coder:14b` | Both Audit and Coding agents |
| Embeddings | `nomic-embed-text` | Vector representation of iteration records |
| Vector store | [ChromaDB](https://www.trychroma.com) | Persistent retrieval store |
| API layer | Flask | HTTP endpoints for n8n to call |
| Spec workflow | [OpenSpec](https://github.com/Fission-AI/OpenSpec) | Spec-driven design of components |
| Runtime | Python 3.13, PowerShell | — |

Everything runs locally. No API keys required.

---

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- [Ollama](https://ollama.com/download) installed and running
- n8n installed globally or via `npx`

### 1. Pull Ollama models

```powershell
ollama pull qwen2.5-coder:14b
ollama pull nomic-embed-text
```

### 2. Install Python dependencies

```powershell
py -m pip install flask chromadb requests pyyaml arxiv pypdf
```

### 3. Start the Flask API

```powershell
py api_trigger.py
```

Verify it's alive:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/health"
```

Expected: `{ status: "healthy", ollama: "connected", chromadb: "connected", flask: "running" }`

### 4. Allow n8n file access

n8n restricts file operations by default. Set the following environment variable **before** starting n8n:

```powershell
$env:N8N_RESTRICT_FILE_ACCESS_TO = "C:\path\to\Code-Improver-Hermes;C:\Users\<you>\.n8n-files"
```

### 5. Start n8n

```powershell
npx n8n
```

This launches the n8n server at `http://localhost:5678`. Leave the terminal running.

### 6. Import the workflow

1. Open n8n (`http://localhost:5678`).
2. **Workflows → Import from File** → select `n8n_workflow.json`.
3. Confirm the SSH/HTTP credentials and paths match your machine.

### 7. Run it

1. Write your task into `data/prompt.md`:
   ```
   Write fibonacci sequence code in JAVA language. Stop condition is 10 rounds of fibonacci sequence.
   ```
2. In n8n, click **Execute Workflow**.
3. Watch the loop execute. Check `data/iterations/<task>/` and `src/<task>/` for output.

---

## API Reference

| Endpoint | Method | Purpose |
| :--- | :--- | :--- |
| `/api/health` | GET | Ollama + ChromaDB connectivity check |
| `/api/prompt` | GET | Read `data/prompt.md` |
| `/api/context` | GET | Query ChromaDB (`?task_name=&query=&top_k=`) |
| `/api/ingest` | POST | Chunk + embed a record (`{record_path, task_name}`) |
| `/api/ensure_dir` | POST | Create a directory (`{path}`) |
| `/api/iteration/<task>/<n>` | GET/POST | Read/write iteration records |

---

## Design decisions

**Why two agents instead of one?**
Separating audit from code generation keeps each prompt focused. An audit prompt that only outputs a numbered list is easier to constrain than one that also produces code. It also lets you swap models independently.

**Why ChromaDB and not a filesystem grep?**
Iteration records describe *what changed and why*. Semantic retrieval surfaces relevant past improvements even when the wording differs from the current task.

**Why `format: "json"` on the record keeper?**
Ollama enforces JSON grammar at the token level. This eliminates the "Here is the JSON you requested:" preamble that breaks every JSON parser downstream.

**Why `$itemIndex` was replaced with an explicit iteration counter**
n8n's `splitInBatches` node returns `$itemIndex = 0` when `batchSize: 1`, because each batch contains exactly one item. The correct iteration number comes from the `For Loop` node's emitted item, not the batch node's index.

---

## Lessons learned

The pipeline works. Getting it there surfaced a handful of issues worth documenting:

- **IPv4 vs IPv6 on Windows.** Node.js resolves `localhost` to `::1` by default; Flask and Ollama listen on `127.0.0.1`. Every HTTP call from n8n must use the explicit IPv4 address.
- **BOM encoding from PowerShell redirection.** `Get-Content | ollama run ... > file.py` writes UTF-16 with a BOM, which Python rejects. Save files as UTF-8 without BOM via VS Code's "Save with Encoding" command.
- **n8n sandbox restrictions.** `child_process`, `fs`, and other Node built-ins are disabled in Code nodes. File operations must go through the `Read/Write Files from Disk` node or an external HTTP API.
- **Pairing loss through Merge nodes.** `$('NodeName').item` relies on n8n's item-pairing metadata, which is destroyed by combining branches. Use `.first()` when referencing nodes from outside the current item's lineage.
- **Template literal escapes.** Backticks inside a template literal terminate it. JSON payloads with nested code blocks must use plain-text delimiters (`---BEGIN CODE---`) instead of markdown fences.
- **n8n file access restrictions.** Since n8n v1.x, file operations are restricted to `~/.n8n-files` unless `N8N_RESTRICT_FILE_ACCESS_TO` is set.

---

## Limitations

- Sequential execution only — no parallel task queue.
- Single-task workflow; no multi-tenant support.
- Windows-first (paths, PowerShell, SSH launch). Linux/macOS requires path adjustments.
- No rollback if the Coding Agent produces invalid code — the loop keeps going, and the last iteration wins.
- Ollama timeouts (5–10 min) mean a full 5-iteration run takes 20–60 minutes on consumer hardware.

---

## Possible extensions

- RAG over external sources (ArXiv, local PDFs) to give the audit agent broader context.
- MCP server exposing the RAG store as a tool for other LLM clients.
- SQLite-backed run history for cross-task analysis.
- Sub-workflow extraction once the topology stabilizes.

---

## License

MIT
```