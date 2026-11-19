# Complete setup and testing guide

Adapted from the supplied Atlas setup guide. These instructions describe the intended system; the current repository is still at the foundation checkpoint. Commands requiring unimplemented modules are clearly marked.

## 1. Create the Python environment

```powershell
conda create -n atlas python=3.12 -y
conda activate atlas
python -m pip install -r requirements.txt
python --version
python -m pip check
```

Skip environment creation if it already exists.

## 2. Configure AWS IAM

1. Sign in to the [AWS Console](https://console.aws.amazon.com/).
2. For a local demo, configure a dedicated identity or temporary credentials. If an IAM access key is needed, create it under IAM → Users → Security credentials.
3. Grant only project-bucket S3 permissions (such as PutObject/GetObject) and selected Bedrock model invocation permissions. Additional permissions depend on the implementation. Prefer a workload role on EC2.
4. Keep credentials secure; never commit them.
5. Select us-east-1, or the actual region of the services/models.

## 3. Configure Amazon Bedrock

1. Open [Amazon Bedrock](https://console.aws.amazon.com/bedrock/) in the selected region.
2. Check that the chosen models or inference profiles can be invoked with your account and role.
3. The original guide targets Amazon Titan Text Embeddings V2 (amazon.titan-embed-text-v2:0; 1024 dimensions) and Nova Lite (amazon.nova-lite-v1:0).
4. **Current code difference:** app/config.py defaults to global.cohere.embed-v4:0 and us.amazon.nova-2-lite-v1:0; Test/test.py uses a Cohere-style embedding payload. The .env.example contains Titan and a differing Nova ID. Align the model, request/response format and access before testing. Do not use the Titan ID with the existing Cohere test payload.

Run the existing smoke test only once the local model configuration is compatible:

```powershell
python Test/test.py
```

Expected: an embedding of the selected dimension and a text answer. API usage may incur charges. The test does not use the shared AWS client yet.

## 4. Create S3 bucket and configure CORS

1. Open [Amazon S3](https://console.aws.amazon.com/s3/) → Create bucket.
2. Choose a globally unique name and the configured region; leave Block all public access enabled and enable encryption.
3. Open bucket → Permissions → Cross-origin resource sharing (CORS) → Edit.
4. Save the following configuration for the local browser-to-S3 PUT upload design.

```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["PUT"],
    "AllowedOrigins": [
      "http://127.0.0.1:8000",
      "http://localhost:8000"
    ],
    "ExposeHeaders": ["ETag"],
    "MaxAgeSeconds": 3000
  }
]
```

The source guide identifies this as the fix for an earlier browser Failed to fetch error. It does not establish that presigned upload works in this repository: the route and browser client are still pending. Use the exact deployed frontend origin when it changes.

## 5. Configure Pinecone

1. Open [Pinecone Console](https://app.pinecone.io/) and create an API key.
2. The target design creates the index automatically; confirm quota and permissions for index creation.
3. Intended configuration: dense vectors, dimension 1024, cosine similarity, serverless AWS us-east-1.
4. The supplied guide calls the index atlas-rag-index. Current Settings defaults to enterprise-qa-index. Choose one consistent PINECONE_INDEX_NAME.
5. Do not assume automatic index creation is implemented: app/vector.py is empty. Implement and validate it in Step 8 of the implementation roadmap.

## 6. Configure Render PostgreSQL

1. Open [Render Dashboard](https://dashboard.render.com/).
2. Select New → Postgres if provisioning is required.
3. Obtain the External Database URL for local development and configure DATABASE_URL.
4. Require SSL; add ?sslmode=require or &sslmode=require as appropriate if not already specified.
5. Securely rotate any previously exposed credentials. URL-encode special characters in passwords where needed.
6. Optionally connect through [VS Code SQLTools](09-render-postgresql-vscode-sqltools.md).

## 7. Configure GlassFlow Rius

The target design uses [GlassFlow Rius](https://www.glassflow.ai/rius). Obtain your API key and reserve the following environment settings:

```dotenv
RIUS_API_KEY=YOUR_RIUS_API_KEY
RIUS_SERVICE_NAME=atlas-ai-enterprise
RIUS_DISABLED=false
RIUS_CAPTURE_CONTENT=false
```

Keep content capture disabled by default. The actual observability integration is pending; these settings alone will not send traces.

## 8. Create the local .env

```powershell
Copy-Item .env.example .env
```

Illustrative configuration with placeholders (never commit real values):

```dotenv
AWS_ACCESS_KEY_ID=YOUR_AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_ACCESS_KEY
AWS_SESSION_TOKEN=
AWS_REGION=us-east-1
S3_BUCKET=YOUR_PRIVATE_BUCKET
DATABASE_URL=postgresql://USER:PASSWORD@HOST/DATABASE?sslmode=require
PINECONE_API_KEY=YOUR_PINECONE_API_KEY
PINECONE_INDEX_NAME=atlas-rag-index
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1
PINECONE_READY_TIMEOUT=180
BEDROCK_EMBED_MODEL=global.cohere.embed-v4:0
BEDROCK_CHAT_MODEL=us.amazon.nova-2-lite-v1:0
EMBED_DIM=1024
HITL_ENABLED=true
MEMORY_TURNS=6
RIUS_API_KEY=YOUR_RIUS_API_KEY
RIUS_SERVICE_NAME=atlas-ai-enterprise
RIUS_DISABLED=false
RIUS_CAPTURE_CONTENT=false
```

The model examples above intentionally follow committed Settings defaults to match the existing smoke-test format, not the original Titan/Nova guide. Availability must be verified. For temporary AWS credentials, add a typed aws_session_token setting before using the current shared client; it is missing today. The auto-create approach uses index name rather than PINECONE_INDEX_HOST. Rius fields also need typed settings and implementation.

Safe configuration check:

```powershell
python -c "from app.config import settings; s=settings(); print(s.aws_region, s.embed_dim, s.pinecone_index_name, bool(s.database_url))"
```

Do not run the existing root test.py in a shared terminal: it prints secrets.

## 9. Initialize PostgreSQL

```powershell
python scripts/init_db.py
```

Expected: success and five verified tables: documents, feedback, audit_events, approvals and chat_messages. Existing rows are preserved on rerun with the supplied schema. If it fails, check instance availability, credentials, SSL and network reachability. See [database foundation](04-database-foundation.md).

## 10. Run the application (planned)

Once app/main.py and the routes are implemented:

```powershell
uvicorn app.main:app --reload
```

Target URLs from the setup guide:

| Feature | Local URL |
| --- | --- |
| App | http://127.0.0.1:8000 |
| API docs | http://127.0.0.1:8000/api/docs |
| Liveness | http://127.0.0.1:8000/health/live |
| Readiness | http://127.0.0.1:8000/health/ready |

These are intended routes; the current empty module cannot serve them. Stop the future server with Ctrl+C.

## 11. End-to-end validation (planned)

Upload a test document; wait for ready status; ask questions that can be answered from it and verify citations; ask a follow-up; test an injection pattern and sensitive action; verify pending approval and audit state; review Rius traces with content capture disabled. Confirm the browser chat scrolls to new messages. No such test run was performed as part of this documentation update.
