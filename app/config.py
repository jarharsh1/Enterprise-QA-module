from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env",extra="ignore")

    ### Application configuration -- General application settings
    aws_access_key_id:str = ""
    aws_secret_access_key:str = ""
    aws_region:str = "us-east-1"
    s3_bucket:str = ""
    
    ## Bedrock configuration 
    bedrock_embed_model:str = 'global.cohere.embed-v4:0'
    bedrock_chat_model:str = 'us.amazon.nova-2-lite-v1:0'
    embed_dim:int = 1024
    max_upload_bytes:int = 10485760

    ## Pinecone configuration -- Vector database connection for the application
    pinecone_api_key:str = ""
    pinecone_index_name:str = "enterprise-qa-index"
    pinecone_cloud:str = "aws"
    pinecone_region:str = "us-east-1"
    pinecone_ready_timeout:int = 180

    ## Application configuration -- Application specific settings
    min_relevance:float = 0.25
    hitl_enabled:bool = True
    memory_turns:int = 6

    ## DATASET configuration -- Dataset specific settings
    database_url:str = ""

@lru_cache()
def settings() -> Settings:
    return Settings()

