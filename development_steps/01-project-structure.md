# Step 01 — Project scaffolding and Python environment

**Source:** [create_structure.py](../create_structure.py), [requirements.txt](../requirements.txt), [README.md](../README.md). Initial scaffold: [f911222](https://github.com/jarharsh1/Enterprise-QA-module/commit/f911222b58d8f99eda4ab32cd15928148c3a3f87), 17 November 2026.

## Objective

Separate application code, document ingestion, infrastructure, scripts and presentation assets before implementing the QA pipeline.

## Reproduce

From the repository root:

```bash
conda create -n atlas python=3.12 -y
conda activate atlas
pip install -r requirements.txt
python create_structure.py
```

The structure script uses pathlib.Path.mkdir(parents=True, exist_ok=True) and Path.touch(exist_ok=True). It creates missing directories and files without truncating existing files, though touch can change modification timestamps. The script is optional on a normal clone where the files already exist.

```text
app/
  config.py, db.py, aws.py
  main.py, vector.py, rag.py, memory.py
  guardrails.py, graph.py, observability.py
  templates/index.html
  static/css/styles.css
  static/js/app.js
worker/ingest.py
infra/schema.sql
scripts/init_db.py
docs/SETUP.md
Test/test.py
test.py
requirements.txt
.env.example
```

The real .env is local-only. Copy the example to .env, fill in your own values, and keep it out of version control.

## Why these dependencies?

| Package | Role |
| --- | --- |
| FastAPI, Uvicorn, Jinja2 | Planned HTTP API, server and templates |
| pydantic-settings, python-dotenv | Environment configuration |
| boto3 | AWS service clients |
| psycopg[binary,pool] | PostgreSQL access; pooling is installed but not yet used |
| pypdf, python-docx | Planned document extraction |
| Pinecone | Planned vector storage and retrieval |
| LangGraph | Planned workflow orchestration |
| httpx | HTTP client |
| glassflow-rius | Planned observability |

Use the versions in requirements.txt rather than selecting new ones arbitrarily. Validate the environment with `python --version` and `pip check`. Installation was not executed during this documentation review.

**Next:** [Cloud infrastructure and Bedrock](02-infrastructure-and-bedrock.md).
