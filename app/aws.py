""""
This is for AWS-specific configuration, including the Bedrock LLM and embedding model
The settings are loaded from the .env file and can be accessed via the `settings()` function
"""

import json
from functools import lru_cache
import boto3
from app.config import settings

@lru_cache
def client(service_name):
    """
    Create and cache a boto3 client for the specified AWS service.
    The client is configured using the AWS credentials and region from the settings.
    """
    s= settings() # load the settings from the .env file using the settings() function
    if bool(s.aws_access_key_id) != bool(s.aws_secret_access_key): ##check if both access key and secret key are set, if not raise an error
        raise RuntimeError("Both AWS Access Key ID and Secret Access Key must be set in the configuration.")
    else:
        options = {'region_name':s.aws_region} ## set the region name for the boto3 client using the AWS region from the settings
    
    if s.aws_access_key_id and s.aws_secret_access_key: ## if both access key and secret key are set, add them to the options dictionary
        options['aws_access_key_id'] = s.aws_access_key_id
        options['aws_secret_access_key'] = s.aws_secret_access_key
        if s.aws_session_token:  ## if a session token is set, add it to the options dictionary
            options['aws_session_token'] = s.aws_session_token
    return boto3.client(service_name, **options) ##return a boto3 client for the specified service using the options dictionary
