# Step 03 — Centralized application configuration

**Source:** [app/config.py](../app/config.py), [.env.example](../.env.example), [test.py](../test.py). Commits [8078dad](https://github.com/jarharsh1/Enterprise-QA-module/commit/8078dadabee9bc9b03dcb1ee7932cacdfcfb312f) and [9e1e998](https://github.com/jarharsh1/Enterprise-QA-module/commit/9e1e9985b207b5955fbc1f54cd3cdbd22f69ecc8), 18 November 2026.

## What we built

A Pydantic BaseSettings subclass with SettingsConfigDict(env_file=".env", extra="ignore"). Environment variables and local .env values populate typed fields; process environment values take precedence over the dotenv file. Unknown dotenv fields are ignored. Run from the repository root because the dotenv path is relative.

```python
@lru_cache()
def settings() -> Settings:
    return Settings()
```

The accessor caches the Settings object in the process to avoid repeatedly loading configuration. Restart the process or clear the cache after changing settings.

## Configuration groups

| Group | Fields and defaults |
| --- | --- |
| AWS | aws_access_key_id, aws_secret_access_key, aws_region (us-east-1), s3_bucket |
| Bedrock/upload | bedrock_embed_model (global.cohere.embed-v4:0), bedrock_chat_model (us.amazon.nova-2-lite-v1:0), embed_dim (1024), max_upload_bytes (10485760) |
| Pinecone | pinecone_api_key, pinecone_index_name (enterprise-qa-index), pinecone_cloud (aws), pinecone_region (us-east-1), pinecone_ready_timeout (180) |
| QA policy | min_relevance (0.25), hitl_enabled (True), memory_turns (6) |
| PostgreSQL | database_url |

The QA policy fields are configuration only; they do not yet enforce retrieval, approval or memory behavior. Defaults for credentials and database URL are empty.

## Safe validation

```bash
python -c "from app.config import settings; s=settings(); print(s.aws_region, s.embed_dim, s.pinecone_index_name, bool(s.database_url))"
```

The root test.py prints raw AWS credentials, Pinecone key and database URL. Do not run it in shared terminals, CI or recorded sessions. A future change should replace those prints with presence checks. No secrets are needed in this guide.

## Known inconsistencies

- aws_session_token is referenced by app/aws.py but not declared on Settings.
- PINECONE_INDEX_HOST in the example has no corresponding Settings field; Settings instead defines pinecone_index_name.
- Example model IDs differ from Settings defaults and the smoke-test request format.
- RIUS_* environment values have no typed settings or observability wiring yet.

**Next:** [Database foundation](04-database-foundation.md).
