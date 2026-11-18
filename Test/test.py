
import os
import json
import boto3
from dotenv import load_dotenv

load_dotenv()

client = boto3.client(
    "bedrock-runtime",
    region_name=os.environ["AWS_REGION"],
    aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"]
)

# TEST 1: Cohere Embed V4
embedding_response = client.invoke_model(
    modelId=os.environ["BEDROCK_EMBED_MODEL"],
    body=json.dumps({
        "texts": ["Hello Amazon Bedrock"],
        "input_type": "search_document",
        "embedding_types": ["float"],
        "output_dimension": int(os.getenv("EMBED_DIM", "1024"))
    }),
    contentType="application/json",
    accept="application/json"
)

embedding_data = json.loads(
    embedding_response["body"].read()
)

embedding = embedding_data["embeddings"]["float"][0]

print("Embedding model:", os.environ["BEDROCK_EMBED_MODEL"])
print("Embedding dimensions:", len(embedding))
print("First 5 values:", embedding[:5])


# TEST 2: Amazon Nova 2 Lite
chat_response = client.converse(
    modelId=os.environ["BEDROCK_CHAT_MODEL"],
    messages=[
        {
            "role": "user",
            "content": [
                {"text": "What is the capital of France?"}
            ]
        }
    ],
    inferenceConfig={"maxTokens": 200}
)

print(
    "Nova chat model response:",
    chat_response["output"]["message"]["content"][0]["text"]
)
