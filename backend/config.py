import os
from typing import Final

import boto3
from dotenv import load_dotenv

load_dotenv()
env = os.getenv

# RDS


# S3
S3_CLIENT: Final[boto3.client] = boto3.client(
    "s3",
    aws_access_key_id=env("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=env("AWS_SECRET_ACCESS_KEY"),
    region_name=env("AWS_REGION")
)

BUCKET_NAME: Final[str] = env("S3_BUCKET_NAME")
