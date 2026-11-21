# Development handbook — Atlas Enterprise AI

This handbook separates **what has been implemented** from **what we intend to build**. The code checkpoint is based on [d6e342d](https://github.com/jarharsh1/Enterprise-QA-module/commit/d6e342d) (21 November 2026). The target design follows the Atlas project overview, supplied setup and implementation guides, and application/CI-CD architecture references.

## Part A — Completed development record

| Step | Guide | Status |
| --- | --- | --- |
| 01 | [Project structure and environment](01-project-structure.md) | Scaffold and dependencies |
| 02 | [Cloud infrastructure and Bedrock smoke tests](02-infrastructure-and-bedrock.md) | Tests/configuration present; live resources unverified |
| 03 | [Centralized configuration](03-application-configuration.md) | Implemented; alignment needed |
| 04 | [PostgreSQL schema and initialization](04-database-foundation.md) | Implemented; execution unverified |
| 05 | [Database access and auditing](05-database-access.md) | Helpers implemented |
| 06 | [Reusable AWS clients](06-aws-client.md) | Client factory; missing session-token field |
| 07 | [Progress and validation](07-progress-and-validation.md) | Known gaps and source history |

## Part B — Practical build and setup guides

| Guide | Purpose |
| --- | --- |
| [08 — Complete setup and testing](08-complete-setup-and-testing-guide.md) | Console setup, local environment, CORS, database initialization and validation |
| [09 — Render PostgreSQL and SQLTools](09-render-postgresql-vscode-sqltools.md) | Connect VS Code to the database securely |
| [10 — Implementation order](10-atlas-implementation-steps.md) | All 26 original build steps, with current statuses |
| [11 — AWS CI/CD deployment](11-aws-cicd-deployment.md) | Planned Docker, GitHub Actions, ECR and EC2 pipeline |

## Architecture

See the [main README](../README.md#target-application-architecture) for simplified target application and deployment diagrams.

At the current checkpoint, Phase 1 (settings, database helpers, schema initializer, Bedrock smoke test, AWS client factory) plus the Phase 2 and Phase 3 code (Pinecone integration, ingestion worker, memory, guardrails, the LangGraph chat pipeline, RAG re-export and the Rius observability module) are all present in source. However, the Phase 2/3 code is **not yet runnable** — several import-time and first-call defects are documented in the [progress checkpoint](07-progress-and-validation.md#blocking-issues-found-in-source-review-phase-23). HITL approval routing, the HTTP API and the UI are still scaffolded. Do not confuse code being present, or a source-guide description, with verified working code in this repository.

## How to maintain this handbook

Update the status in Guide 10 and the progress checkpoint as code lands. Add a numbered development record for each independently meaningful component, documenting its objective, files, commands, testing evidence, limitations and commit. Keep credentials and personal infrastructure identifiers out of this public repository.
