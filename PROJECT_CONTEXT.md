# Project Context

## Overview

This project is a ticket ingestion and RCA-routing system with:

- a static frontend (`index.html`, `script.js`, `styles.css`)
- a FastAPI backend (`backend/`)
- MongoDB storage for tickets, embeddings, workflow state, and RCA results
- S3 artifact storage for uploaded inputs, outputs, and logs
- a Gemini-based structuring step
- an OpenRouter-based RAG routing step
- an OpenCode-based RCA plan step

The current intended flow is:

1. User submits a ticket with metadata, description, and optional screenshots.
2. Backend uploads images/input artifacts to S3 and stores the initial ticket in MongoDB.
3. Gemini structuring analyzes text + screenshots into a normalized incident record.
4. A summary embedding is generated and stored in MongoDB.
5. A RAG agent uses vector retrieval over recent incidents to decide the next flow.
6. If a similar incident is found, the ticket is marked as matched and RCA is skipped.
7. If not, OpenCode runs in plan mode against a repo and writes an RCA report back to MongoDB.

## Current Architecture

### Frontend

- `index.html`
  - static form-based UI
  - captures request metadata, issue description, route, review type, and images
  - has a live analysis panel

- `script.js`
  - checks backend health via `GET /health`
  - submits to `POST /api/tickets/ingest`
  - polls `GET /api/tickets/{request_id}`
  - renders:
    - processing state
    - structured output
    - embedding status
    - RAG status
    - dedup / RCA state
    - status history

- `styles.css`
  - UI styling only

### Backend

- `backend/server.py`
  - Uvicorn entrypoint
  - now has logging setup

- `backend/api.py`
  - main FastAPI app
  - startup dependency checks for MongoDB and S3
  - health endpoint
  - ingest endpoint
  - ticket fetch endpoint
  - vector search endpoint
  - background processing pipeline

- `backend/ingestion_ticket.py`
  - Gemini-based multimodal structuring
  - uses uploaded screenshots + issue description
  - produces normalized JSON fields
  - builds `embedding_text`

- `backend/embedder.py`
  - summary embedding generation
  - MongoDB vector index definition
  - vector search pipeline builder

- `backend/db.py`
  - MongoDB connection and collection helpers
  - standard indexes
  - Atlas vector index creation attempt

- `backend/opencode_orchestrator.py`
  - RAG routing agent
  - OpenRouter model usage
  - vector retrieval over MongoDB
  - structured flow decision output
  - OpenCode invocation
  - MongoDB workflow/result updates

- `backend/s3_upload.py`
  - uploads images, input JSON, output JSON, and logs to S3

- `backend/s3get.py`
  - helper around S3 access

- `backend/langchain_test.py`
  - appears to be a local experiment / example file for LangChain + OpenRouter

## Current Runtime Responsibilities

### Structuring Agent

The structuring agent should only:

- analyze input text + screenshots
- extract visible evidence
- normalize the incident record
- build the embedding text
- store the summary embedding

It should not decide:

- whether to reuse an old incident
- whether to run RCA
- whether to invoke OpenCode

Those decisions are now intended to belong to the RAG routing step.

### RAG Agent

The RAG agent in `backend/opencode_orchestrator.py` is responsible for:

- taking the structured summary / embedding text
- querying MongoDB vector search
- using OpenRouter in a LangChain agent loop
- producing a final structured decision JSON:
  - `reuse_existing_incident`
  - `opencode_rca`

### OpenCode RCA

When RAG selects RCA, the system sends OpenCode:

- structured incident data
- MongoDB ticket context
- stored input/output/log artifact references
- repository analysis brief

It does not send raw model output to OpenCode anymore.

## Models In Use

### Gemini

Used only in:

- `backend/ingestion_ticket.py`

Purpose:

- multimodal understanding for ticket structuring

### OpenRouter

Used in:

- `backend/opencode_orchestrator.py`

Model configured:

- `nvidia/nemotron-3-super-120b-a12b:free`

Purpose:

- RAG routing decision
- repository analysis brief generation
- structured JSON routing output

### Embedding Model

Used in:

- `backend/embedder.py`

Current default:

- `OLLAMA_EMBEDDING_MODEL`, fallback `nomic-embed-text-v2-moe:latest`

Purpose:

- create summary embeddings for vector retrieval

## Data Stored In MongoDB

Each ticket currently stores:

- basic request metadata
- form payload
- intake metadata
- storage metadata
- artifact URLs
- analysis output
- normalized triage fields
- embedding record
- workflow state
- RCA result
- status history

Important nested fields:

- `analysis.structured`
- `analysis.embeddingText`
- `embeddings.summary`
- `workflow.rag`
- `workflow.dedup`
- `workflow.rca`
- `rca.result`
- `statusHistory`

## Current Workflow State Shape

### `workflow.rag`

Used to track:

- `not_started`
- `pending`
- `running`
- `completed`

### `workflow.dedup`

Used to track:

- `not_started`
- `waiting_for_rag`
- `matched`
- `no_match`

### `workflow.rca`

Used to track:

- `not_applicable`
- `waiting_for_rag`
- `skipped_duplicate`
- `completed`
- `failed`

## Current Retrieval Rules

Vector retrieval is currently constrained to:

- only incidents from the last 60 days
- only incidents with the same `reviewType`
- only records where `embeddings.summary.status == "completed"`

## Current File / Repo Assumptions

The automatic OpenCode step assumes:

- the repository to inspect exists locally at:
  - `C:\Users\Administrator\mamba\image`

This is configurable with environment variables:

- `OPENCODE_REPO_DIR`
- `OPENCODE_BIN`

If the repo is missing:

- RAG still runs
- the ticket is updated with a clean RCA failure
- the whole pipeline should not crash anymore

## Current Frontend Behavior

The frontend now shows:

- processing status
- structured summary
- error type / system / page / severity
- image evidence
- embedding status
- RAG routing status
- parsed RAG decision JSON
- dedup match state
- RCA state
- OpenCode exit code
- status history
- raw stored structured output JSON

## Current Logging

Logging has been added to:

- `backend/server.py`
- `backend/api.py`
- `backend/ingestion_ticket.py`
- `backend/opencode_orchestrator.py`

Current logged milestones include:

- startup dependency checks
- background processing start
- structuring start / completion
- embedding start / success / failure
- artifact save
- ticket update after structuring
- vector retrieval
- RAG decision
- OpenCode launch / completion
- failure traces

## Known Issues / Important Notes

### MongoDB Atlas TLS

The backend has recently hit MongoDB Atlas SSL handshake failures. Startup is now tolerant of this and exposes degraded health instead of crashing, but the underlying Atlas connectivity problem is still external and unresolved.

### Health Endpoint Semantics

`GET /health` now returns:

- `ok` when dependencies are healthy
- `degraded` when backend is running but Mongo or S3 is unavailable

The frontend treats degraded as backend-up.

### Structuring Quality

The structuring prompt has been updated to extract more screenshot detail, but if extraction is still too generic the next place to improve is:

- image preprocessing
- prompt examples
- adding OCR-specific extraction before Gemini

### OpenCode Dependency

If RAG selects OpenCode but:

- the repo directory does not exist, or
- `opencode` is not on PATH,

the RCA branch will fail and this should be reflected in MongoDB and frontend status.

## Important Files

Top-level:

- `index.html`
- `script.js`
- `styles.css`
- `pyproject.toml`
- `run_opencode_plan.sh`
- `full_project_plan.html`

Backend:

- `backend/server.py`
- `backend/api.py`
- `backend/db.py`
- `backend/embedder.py`
- `backend/ingestion_ticket.py`
- `backend/opencode_orchestrator.py`
- `backend/s3_upload.py`
- `backend/s3get.py`
- `backend/.env`

## Current Python Dependencies

Important packages currently relevant to the architecture:

- `fastapi`
- `uvicorn`
- `pymongo`
- `langchain`
- `langchain-google-genai`
- `langchain-openrouter`
- `langchain-openai`
- `langchain-mongodb`
- `langchain-ollama`
- `openai`
- `boto3`
- `python-multipart`
- `pillow`

## Workspace State

Current workspace contains modified files and untracked artifacts. It is not a clean git worktree.

Modified:

- `backend/api.py`
- `backend/ingestion_ticket.py`
- `backend/opencode_orchestrator.py`
- `backend/server.py`
- `index.html`
- `pyproject.toml`
- `script.js`
- `styles.css`
- `uv.lock`

Untracked:

- `full_project_plan.html`
- `run_opencode_plan.sh`
- `screenshot.png`

## Short Summary

This is currently a hybrid system where:

- frontend captures tickets
- backend structures them with Gemini
- embeddings are stored in MongoDB
- an OpenRouter-based RAG agent decides reuse vs RCA
- OpenCode is used only when RAG selects RCA
- MongoDB and S3 are required for full functionality
- the frontend now exposes most of the workflow state

The biggest operational risk right now is not Python syntax but external dependency reliability:

- MongoDB Atlas connectivity
- S3 availability
- presence of the local repo for OpenCode RCA
