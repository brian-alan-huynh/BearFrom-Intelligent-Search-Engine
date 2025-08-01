import os
import uuid
from dotenv import load_dotenv

import openai
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec

load_dotenv()
env = os.getenv

pc = Pinecone(api_key=env("PINECONE_API_KEY"))
index_name = env("PINECONE_INDEX_NAME")

if not pc.has_index(index_name):
    pc.create_index(
        name=index_name,
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region=env("PINECONE_INDEX_REGION")
        ),
        deletion_protection="disabled",
        tags={"project": "huggypanda-rag-search"}
    )
    
index = pc.Index(index_name)

openai.api_key = env("OAI_API_KEY")

def convert_to_vector_embed(texts: list[str]) -> list[list[float]]:
    response = openai.embeddings.create(
        model="text-embedding-3-small",
        input=texts,
    )
    
    return [e.embedding for e in response.data]

def add_to_vector_db(texts: list[str], vector_embeds: list[list[float]]) -> str:
    try:
        namespace = str(uuid.uuid4())
        count = 0
        
        for text, vector_embed in zip(texts, vector_embeds):
            vector_id = namespace + "_vector" + str(count)
            
            vector_data = {
                "id": vector_id,
                "values": vector_embed,
                "metadata": {"original_text": text}
            }
            
            count += 1
        
            index.upsert(vectors=[vector_data], namespace=namespace)
        
        return namespace # store as variable in route to be used in query_from_vector_db()
    
    except Exception as e:
        return f"Failed to add to vector database ({e})"

def convert_query_to_vector_embed(query: str) -> list[float]:
    response = openai.embeddings.create(
        model="text-embedding-3-small",
        input=query,
    )
    
    return response.data[0].embedding

def query_from_vector_db(vector_query: list[float], namespace: str) -> list[str]:
    try:
        results = index.query(
            vector=vector_query,
            namespace=namespace,
            top_k=5,
            include_metadata=True,
            include_values=False,
        )
        
        return [result.metadata.original_text for result in results.matches]
    
    except Exception as e:
        return f"Failed to query vector database ({e})"

def delete_from_vector_db(namespace: str) -> None: # when a new query happens, the last_pinecone_vector_namespace is updated in Redis with the new vector namespace. the last vector namespace is called as a parameter to this function
    index.delete(namespace=namespace)
