import os
from typing import Final

import boto3
from dotenv import load_dotenv
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec

load_dotenv()
env = os.getenv

# S3
S3_CLIENT: Final[boto3.client] = boto3.client(
    "s3",
    aws_access_key_id=env("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=env("AWS_SECRET_ACCESS_KEY"),
    region_name=env("AWS_REGION")
)

BUCKET_NAME: Final[str] = env("S3_BUCKET_NAME")

# Pinecone
PC: Final[Pinecone] = Pinecone(api_key=env("PINECONE_API_KEY"))
PC_INDEX_NAME: Final[str] = env("PINECONE_INDEX_NAME")

if not PC.has_index(PC_INDEX_NAME):
    PC.create_index(
        name=PC_INDEX_NAME,
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region=env("PINECONE_INDEX_REGION")
        ),
        deletion_protection="disabled",
        tags={"project": "huggypanda-rag-search"}
    )

PC_INDEX: Final[Pinecone.Index] = PC.Index(PC_INDEX_NAME)

# 
