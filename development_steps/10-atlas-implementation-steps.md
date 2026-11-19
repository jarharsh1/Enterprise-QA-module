# Atlas Enterprise AI — Step-by-step implementation order

The 26 steps below retain the supplied Atlas implementation guide's sequence. Status reflects the committed source checkpoint dea3d34, not a live cloud environment. See [current build record](07-progress-and-validation.md).

## Phase 1 — Setup and infrastructure

| Step | File / component | What to develop | Current status |
| --- | --- | --- | --- |
| 1 | requirements.txt | Dependencies: FastAPI, LangGraph, boto3, Pinecone, PostgreSQL, Rius | Implemented |
| 2 | .env.example → .env | AWS, S3, model, Pinecone, Render and Rius settings; never commit .env | Template present; local setup unverified, alignment needed |
| 3 | app/config.py | Typed centralized settings | Implemented; missing session token and Rius settings |
| 4 | infra/schema.sql | Documents, chat_messages, approvals, feedback, audit_events | Implemented |
| 5 | app/db.py | Connection and audit helpers | Implemented |
| 6 | scripts/init_db.py | Initialize and verify five tables | Implemented; execution unverified |
| 7 | app/aws.py | Shared AWS clients, S3 operations, Bedrock chat and embeddings | Partial: cached client only; standalone Bedrock test exists |
| 8 | app/vector.py | Pinecone auto-create, upsert, similarity search | Pending |

**Next development step:** Finish Step 7, including configuration fixes, shared model wrappers and S3 helpers; then implement Step 8. The original design uses Titan V2/Nova Lite, whereas current code uses different default model IDs. Decide which compatible models to use before writing wrappers.

## Phase 2 — Document ingestion and RAG

| Step | File | What to develop | Status |
| --- | --- | --- | --- |
| 9 | worker/ingest.py | Download S3 object, extract text, chunk, embed, upsert, update PostgreSQL status; explicitly invoke worker | Pending |
| 10 | app/rag.py | Retrieval and grounded-answer helpers; inspect actual implementation rather than assume re-export | Pending |
| 11 | app/memory.py | Persist and retrieve recent conversation turns | Pending; SQL table exists |
| 12 | app/guardrails.py | Deterministic input/output checks for injection, secrets and unsafe responses | Pending |
| 13 | app/graph.py | LangGraph orchestration: checks, memory/retrieval, generation, HITL routing and output checks | Pending |

Target ingestion flow: S3 → worker → extraction/chunking → Bedrock embeddings → Pinecone → PostgreSQL status. Target chat flow: user question → input checks → history and relevant chunks → generation → output checks → cited answer. Sensitive actions create approval records; approval itself does not execute deletion or policy modification.

## Phase 3 — Observability with GlassFlow Rius

| Step | File / component | What to develop | Status |
| --- | --- | --- | --- |
| 14 | app/observability.py | Optional tracing, service name, API key, privacy-safe settings | Pending |
| 15 | app/graph.py | Trace agent nodes, latency and errors | Pending |
| 16 | app/aws.py, app/vector.py | Instrument model calls and vector operations | Pending |
| 17 | worker/ingest.py | Trace ingestion stages and failures | Pending |
| 18 | Rius dashboard | Verify test traces; avoid exporting secrets or sensitive content | Pending |

## Phase 4 — FastAPI and UI

| Step | File | What to develop | Status |
| --- | --- | --- | --- |
| 19 | app/main.py | Presigned URL, ingestion, documents, chat, approval, metrics routes; wire graph and worker | Pending |
| 20 | app/templates/index.html | Chat, upload, documents, approvals and metrics dashboard | Pending |
| 21 | app/static/css/styles.css | Styling and fixed-height scrollable chat history | Pending |
| 22 | app/static/js/app.js | API calls, presigned upload, approvals, chat rendering and auto-scroll | Pending |

## Phase 5 — Integration and validation

| Step | Component | What to develop | Status |
| --- | --- | --- | --- |
| 23 | Amazon S3 CORS | Allow browser PUT from exact permitted origins | Configuration guide available; live unverified |
| 24 | tests/ | Automated upload/ingestion, citations, memory, guardrails, HITL, Rius and UI tests | Pending; two diagnostic scripts exist |
| 25 | docs/SETUP.md, docs/RIUS_OBSERVABILITY.md | Setup, privacy, testing, troubleshooting | Partial: development handbook exists; original setup empty, Rius guide absent |
| 26 | End-to-end demo | Initialize DB, start API, upload, chat, test governance and review traces | Pending |

## Phase 6 — CI/CD deployment (architecture extension)

The supplied deployment diagram adds GitHub Actions, Docker, Amazon ECR and EC2. This is an extension after the original 26 implementation steps, not a completed feature. See [AWS CI/CD plan](11-aws-cicd-deployment.md).

## Acceptance principles

Document the code, run the relevant smoke or automated tests, record results and update this guide after each step. Tenant metadata and guardrail patterns alone do not establish production-grade isolation or full security. Authentication, authorization and enforcement remain necessary.
