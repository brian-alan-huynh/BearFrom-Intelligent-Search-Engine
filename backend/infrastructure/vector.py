import os
import uuid
from dotenv import load_dotenv

import openai
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec

load_dotenv()
env = os.getenv

openai.api_key = env("OAI_API_KEY")
class Vector:
    def __init__(self):
        self.pc = Pinecone(api_key=env("PINECONE_API_KEY"))
        self.index_name = env("PINECONE_INDEX_NAME")

        if not self.pc.has_index(self.index_name):
            self.pc.create_index(
                name=self.index_name,
                dimension=1536,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region=env("PINECONE_INDEX_REGION")
                ),
                deletion_protection="disabled",
                tags={"project": "huggypanda-rag-search"}
            )

        self.index = self.pc.Index(self.index_name)
        self.openai = openai

    def convert_to_vector_embed(self, texts: list[str]) -> list[list[float]]:
        response = self.openai.embeddings.create(
            model="text-embedding-3-small",
            input=texts,
        )
    
        return [e.embedding for e in response.data]

    def add_to_vector_db(self, texts: list[str], vector_embeds: list[list[float]]) -> str | bool: # use kafka
        try:
            namespace = str(uuid.uuid4())
            count = 0
            
            for text, vector_embed in zip(texts, vector_embeds):
                vector_id = namespace + "_vector" + str(count)
                
                vector_data = [{
                    "id": vector_id,
                    "values": vector_embed,
                    "metadata": {"original_text": text}
                }]
        
                self.index.upsert(vectors=vector_data, namespace=namespace)
                count += 1
        
            return namespace
    
        except Exception as e:
            return False

    def convert_query_to_vector_embed(self, query: str) -> list[float]:
        response = self.openai.embeddings.create(
            model="text-embedding-3-small",
            input=query,
        )
    
        return response.data[0].embedding

    def query_from_vector_db(self, vector_query: list[float], namespace: str) -> list[str] | bool:
        try:
            results = self.index.query(
                vector=vector_query,
                namespace=namespace,
                top_k=5,
                include_metadata=True,
                include_values=False,
            )
        
            return [
                f"{count}. {result['metadata']['original_text']}" 
                for count, result in enumerate(results['matches'], start=1)
            ]
    
        except Exception as e:
            return False

    def delete_from_vector_db(self, namespace: str) -> None: # use kafka
        self.index.delete(namespace=namespace)
