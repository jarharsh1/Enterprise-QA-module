# Step 06 — Reusable AWS client factory

**Source:** [app/aws.py](../app/aws.py), [app/config.py](../app/config.py). Commit [dea3d34](https://github.com/jarharsh1/Enterprise-QA-module/commit/dea3d34dc312f0364d12c871eaaacfd73b16cd80), 18 November 2026.

## Objective and implementation

Centralize AWS client creation so future S3 and Bedrock modules use a consistent region and credential policy instead of duplicating boto3 setup.

The client(service_name) function is decorated with lru_cache. It loads Settings, compares the presence of access and secret keys, rejects partially supplied credentials, initializes region_name, adds explicit credentials if both are supplied, optionally attempts to add a session token, and returns boto3.client(service_name, **options).

If neither explicit key is supplied, the boto3 default credential provider chain can supply credentials (for example from an execution role). Successful calls for the same service name reuse a cached client within the process. This is a client factory, not an embedding or chat invocation wrapper.

## Intended usage

```python
from app.aws import client

s3 = client("s3")
bedrock = client("bedrock-runtime")
```

These are intended call sites; no service operation is performed simply by assigning a client. Client construction may still resolve credentials or fail due to local credential configuration.

## Blocking issue found in source review

With explicit access and secret keys, the code reaches s.aws_session_token. Settings does not declare this attribute, so that branch can raise AttributeError before boto3.client is called. The recommended correction is to declare an optional aws_session_token field in Settings and document its environment variable. This guide does not modify application code.

The standalone Bedrock smoke test does not use this factory, so success of that script would not prove the factory works.

## Validation after remediation

Test with mocked boto3.client: both keys absent, both keys supplied, only one key supplied (expect RuntimeError), and temporary credentials with a session token. Verify repeated calls reuse the same client and different service names create different clients. Clear both caches between independent configuration tests. Then run a restricted live service smoke test with valid credentials if required.

**Next:** [Progress and validation checkpoint](07-progress-and-validation.md).
