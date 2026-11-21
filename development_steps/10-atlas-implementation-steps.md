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
| 7 | app/aws.py | Shared AWS clients, S3 operations, Bedrock chat and embeddings | Client factory done; embed()/answer() wrappers added but broken (wrong Bedrock client/API, Titan payload vs Cohere model, `embedding_dimensions` typo, session-token field still missing) |
| 8 | app/vector.py | Pinecone auto-create, upsert, similarity search | Implemented; describe/create, tenant namespaces, ACL-filtered search present; readiness-timeout loop is a no-op; unverified live |

**Next development step:** The embedding/answer wrappers (Step 7) exist but do not match the configured model or the correct Bedrock API — correct these and the session-token field first. The original design uses Titan V2/Nova Lite, whereas current code defaults to Cohere Embed v4 / Nova 2 Lite. Lock one compatible model set before fixing the wrappers.

## Phase 2 — Document ingestion and RAG

| Step | File | What to develop | Status |
| --- | --- | --- | --- |
| 9 | worker/ingest.py | Download S3 object, extract text, chunk, embed, upsert, update PostgreSQL status; explicitly invoke worker | Implemented; S3 fetch, PDF/DOCX/text parse, chunking, batched upsert, `pending→processing→ready/failed` transitions and audit present; blocked at runtime by the broken embed() and observability initialize() |
| 10 | app/rag.py | Retrieval and grounded-answer helpers; inspect actual implementation rather than assume re-export | Implemented as a one-line re-export of `app.graph.chat` (retrieval/answer logic lives in app/graph.py and app/aws.py) |
| 11 | app/memory.py | Persist and retrieve recent conversation turns | Implemented; history/save_turn/list_messages present; `history()` has a `craeted_at` column typo that fails at runtime |
| 12 | app/guardrails.py | Deterministic input/output checks for injection, secrets and unsafe responses | Implemented; input injection and sensitive-output checks done; `check_evidence` is a pass-through and is not called by the graph |
| 13 | app/graph.py | LangGraph orchestration: checks, memory/retrieval, generation, HITL routing and output checks | LangGraph pipeline implemented (guard → retrieve → generate/no_evidence → validate); HITL routing NOT implemented; retrieve() mishandles the Pinecone response and depends on an undefined principal object |

Target ingestion flow: S3 → worker → extraction/chunking → Bedrock embeddings → Pinecone → PostgreSQL status. Target chat flow: user question → input checks → history and relevant chunks → generation → output checks → cited answer. Sensitive actions create approval records; approval itself does not execute deletion or policy modification.

## Phase 3 — Observability with GlassFlow Rius

| Step | File / component | What to develop | Status |
| --- | --- | --- | --- |
| 14 | app/observability.py | Optional tracing, service name, API key, privacy-safe settings | Implemented but broken: `trace()` returns None (breaks every decorated import) and `initialize()` uses non-existent `os.get_env` / wrong `os.get_blocking` |
| 15 | app/graph.py | Trace agent nodes, latency and errors | `@trace` applied to all graph nodes; effectively disabled until the decorator bug is fixed |
| 16 | app/aws.py, app/vector.py | Instrument model calls and vector operations | `@trace` applied to embed/answer/upsert/search; same decorator-bug dependency |
| 17 | worker/ingest.py | Trace ingestion stages and failures | `@trace` on process_s3_key and `initialize()` called at import; blocked by the observability bugs |
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
