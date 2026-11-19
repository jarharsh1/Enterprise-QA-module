# Step 02 — Cloud infrastructure and Bedrock smoke tests

**Source:** [.env.example](../.env.example), [Test/test.py](../Test/test.py), [requirements.txt](../requirements.txt). Infrastructure milestone [f99f099](https://github.com/jarharsh1/Enterprise-QA-module/commit/f99f09941115549340389a3b88399ea335661034), environment template [c109cc5](https://github.com/jarharsh1/Enterprise-QA-module/commit/c109cc51f2b6e5feb24aad5dd5fdae713946e81e), Bedrock test [1dbf9fd](https://github.com/jarharsh1/Enterprise-QA-module/commit/1dbf9fd7edae31e5674624126681ed438d9f1066).

## Objective

Prepare external dependencies separately from the business logic: AWS credentials and region, S3 documents, Bedrock embeddings and generation, Pinecone vectors, PostgreSQL records.

## Infrastructure checklist (manual prerequisites)

1. Configure AWS credentials with least privilege and choose the region.
2. Prepare a private S3 bucket for document storage. Verify scoped access; avoid public buckets.
3. Confirm Bedrock model IDs, inference-profile access and invocation permissions in the selected region.
4. Prepare a Pinecone index with dimensions matching the embedding model and configured retrieval metric.
5. Provision a PostgreSQL instance and obtain a valid connection URL.

The README and commit history indicate an infrastructure milestone, but the repository does not contain provisioning automation or proof of successful cloud creation. The S3, Pinecone and database resources must be verified in their respective consoles.

## Environment groups

Copy .env.example locally. Fill in AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, S3_BUCKET; BEDROCK_EMBED_MODEL, BEDROCK_CHAT_MODEL, EMBED_DIM; PINECONE_API_KEY, PINECONE_CLOUD, PINECONE_REGION, PINECONE_READY_TIMEOUT; DATABASE_URL. RIUS_* variables are reserved for the planned observability module.

**Important:** the example's Titan embedding model differs from the Cohere Embed v4 request format in the smoke test. The example also uses a different Nova ID from app/config.py. Use an accessible model/profile compatible with the actual request payload; do not assume the examples are interchangeable. The test expects Cohere's embeddings.float response. The application settings default to global.cohere.embed-v4:0 and us.amazon.nova-2-lite-v1:0; availability is account/region-dependent.

## Implemented smoke test

From the project root after filling in compatible local settings:

```bash
python Test/test.py
```

The first test creates a bedrock-runtime boto3 client, calls invoke_model with a text list, input_type=search_document, floating-point embeddings and configured output_dimension (default 1024). It reads the response body, extracts the first float vector, and prints the dimensions and first five values.

The second test calls converse with a sample user question and maxTokens=200, then prints the returned answer. Both are direct API smoke tests; neither is yet wrapped in the application client. Running them may incur AWS charges.

## Validation

Expect an embedding of the configured length and a coherent factual answer. Verify that the Pinecone index dimension matches this length before ingestion. These outcomes are expected, not recorded results. The script does not contain assertions or test temporary session-token credentials.

**Next:** [Centralized application settings](03-application-configuration.md).
