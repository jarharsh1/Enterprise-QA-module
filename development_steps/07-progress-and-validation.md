# Step 07 — Progress checkpoint and next implementation steps

Source snapshot: [d6e342d](https://github.com/jarharsh1/Enterprise-QA-module/commit/d6e342d). Reviewed 21 November 2026.

## Chronological build record

| Date | Commit | Work |
| --- | --- | --- |
| Nov 17 | 99da559 | Initial commit |
| Nov 17 | f911222 | Project structure |
| Nov 17 | f99f099 | Infrastructure milestone |
| Nov 17 | c109cc5 | AWS/S3 environment template |
| Nov 18 | 1dbf9fd | Bedrock embedding and chat smoke test |
| Nov 18 | 8078dad | Typed application settings |
| Nov 18 | 9e1e998 | Settings print diagnostic |
| Nov 18 | 8848cfd | Five-table PostgreSQL schema |
| Nov 18 | 7977406 | Database connection and audit helper |
| Nov 18 | b2d6a86 | Database initialization script |
| Nov 18 | dea3d34 | Cached AWS client factory |
| Nov 19 | bfc72ba | Docs: aligned setup guides and target-architecture roadmap |
| Nov 20 | 9ccb996 | psycopg version upgrade |
| Nov 20 | 318ad56 | Bedrock embedding/answer wrappers with observability tracing |
| Nov 20 | 90523ce | Pinecone vector DB configuration (app/vector.py) |
| Nov 21 | d6e342d | Document ingestion worker, memory, guardrails and LangGraph chat pipeline |

See [commit history](https://github.com/jarharsh1/Enterprise-QA-module/commits/main/) for original changes.

## Implementation status

| Component | Status |
| --- | --- |
| Project folders and dependencies | Implemented |
| Environment template and typed settings | Implemented, alignment needed |
| Bedrock smoke-test script | Implemented; live outcome unverified |
| PostgreSQL schema and initializer | Implemented; live outcome unverified |
| Database connection and audit | Implemented; runtime unverified |
| AWS client factory | Implemented; missing session-token field |
| Pinecone integration (app/vector.py) | Implemented; index create/describe, tenant namespaces and ACL-filtered search present; readiness-timeout loop is a no-op; unverified live |
| Document ingestion (worker/ingest.py) | Implemented; S3 fetch, PDF/DOCX/text parse, chunking, embed, batched upsert, status state machine and audit present; depends on broken embed() and observability (see blocking issues); unverified live |
| RAG (app/rag.py) | Implemented as a thin re-export of app.graph.chat |
| Conversation memory (app/memory.py) | Implemented; history/save_turn/list_messages present; history() SQL has a `craeted_at` column typo that will fail at runtime |
| Guardrails (app/guardrails.py) | Implemented; deterministic input injection and sensitive-output checks; check_evidence is a pass-through and is not called by the graph |
| LangGraph/HITL (app/graph.py) | LangGraph pipeline implemented (guard → retrieve → generate/no_evidence → validate); HITL approval routing NOT implemented despite approvals table and hitl_enabled setting; retrieve() mishandles the Pinecone response shape; depends on an undefined principal object |
| Observability (app/observability.py) | Implemented but broken: trace() returns None (breaks every decorated import); initialize() calls non-existent os.get_env / wrong os.get_blocking |
| HTTP API (app/main.py) | Empty placeholder |
| HTML/CSS/JS | Empty placeholders |
| End-to-end deployment and automated tests | Not demonstrated by repository |

## Blocking issues found in source review (Phase 2/3)

These were confirmed against the committed code at d6e342d. Until they are resolved the ingestion worker and chat graph cannot run, because the failures occur at import time or on first call.

1. **Observability decorator is inert (import-breaking).** `app/observability.py` `trace()` returns `None` — its `return decorate` is nested inside `decorate` instead of `trace`. Every `@trace(...)`-decorated function therefore fails with `TypeError: 'NoneType' object is not callable` at import, which breaks `app/aws.py`, `app/vector.py`, `app/graph.py` and `worker/ingest.py`.
2. **`initialize()` uses non-existent APIs.** It calls `os.get_env(...)` (correct name is `os.getenv`) and `os.get_blocking(...)` (a file-descriptor function, not an env reader). `worker/ingest.py` calls `initialize()` at import, so the worker cannot load.
3. **`aws.py embed()` is inconsistent with the configured model.** It reads `settings().embedding_dimensions` (the field is `embed_dim`), calls `client("bedrock")` (invoke_model lives on `bedrock-runtime`), and sends a Titan-style payload (`inputText`/`dimensions`/`normalize`) parsing `['embedding']`, while the configured model is Cohere Embed v4 (expects `texts`/`input_type`/`output_dimension`, returns `embeddings.float`).
4. **`aws.py answer()` mixes two Bedrock APIs.** It calls `invoke_model` with `messages`/`inferenceConfig`, which belong to the Converse API (`client.converse(...)`, with a separate `system` argument). It also builds `recent` by iterating `(history, [])` — a 2-tuple — so `row['role']` is applied to the history list itself; it likely meant `(history or [])`.
5. **`aws_session_token` still undeclared.** Carried over from Phase 1: `app/aws.py` reads `s.aws_session_token` but `Settings` does not define it, so `client()` raises `AttributeError` when both AWS keys are set.
6. **`memory.py history()` column typo.** The inner query selects `craeted_at`; the column is `created_at`, so the query errors at runtime.
7. **`graph.py retrieve()` response handling.** It iterates the Pinecone query result directly and reads `h['score']`/`h['metadata']`; matches are returned under `matches`. It also depends on a `principal` object (`.tenant`, `.groups`, `.subject`) that is not defined anywhere in the repository yet.
8. **`vector.py` readiness loop is a no-op.** `time.monotonic() >= time.monotonic() + timeout` is always false, so the timeout never fires; compute the deadline once before the loop.

## Recommended next steps (not completed)

1. Fix the Phase 2/3 blocking issues above (observability decorator and `initialize()`, the Bedrock embed/answer wrappers, the memory column typo, the Pinecone response handling), then re-run import and smoke checks.
2. Resolve the Settings/session-token mismatch; align model IDs and Pinecone configuration to the chosen embedding model; replace the secret-printing diagnostic.
3. Validate embedding dimensions and chat response parsing against the live Bedrock model once the wrappers are corrected.
4. Wire HITL: add an approval node and routing to the graph that uses the `approvals` table and `hitl_enabled` setting; call `check_evidence` on retrieved passages.
5. Define the `principal` object used by the graph (tenant, groups, subject) and the S3 presigned-upload path that feeds the worker.
6. Add the HTTP API (app/main.py), routes, authentication/authorization and the browser UI.
7. Add unit, integration, security, retrieval-quality and end-to-end tests; establish deployment/operational procedures.

## Exit criteria for the current foundation

- [ ] Dependency installation and import checks pass.
- [ ] Safe settings validation passes without exposing credentials.
- [ ] Bedrock embedding dimension and chat response validated with compatible model IDs.
- [ ] PostgreSQL initializer and five tables verified in test database.
- [ ] Connection/audit success and rollback tested.
- [ ] AWS client credential branches tested after missing-field fix.
- [ ] S3 and Pinecone resources and permissions independently verified.

Unchecked means verification was not performed in this documentation review, not necessarily that the underlying work has failed. This review used committed code and history only; no cloud credentials were accessed, no deployment was executed, and no application source was changed.
