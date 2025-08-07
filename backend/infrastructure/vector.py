import os
import uuid
from dotenv import load_dotenv
import json

import openai

from .messaging import kafka_producer
from ..config import PC_INDEX

load_dotenv()
env = os.getenv

openai.api_key = env("OAI_API_KEY")
class Vector:
    def __init__(self):
        self.openai = openai

    def convert_to_vector_embed(self, texts: list[str]) -> list[list[float]]:
        response = self.openai.embeddings.create(
            model="text-embedding-3-small",
            input=texts,
        )
    
        return [e.embedding for e in response.data]

    def add_to_vector_db(self, texts: list[str], vector_embeds: list[list[float]]) -> str | bool:
        try:
            namespace = str(uuid.uuid4())
            count = 0
            
            for text, vector_embed in zip(texts, vector_embeds):
                vector_id = namespace + "_vector_" + str(count)
                
                message = {
                    "operation": "add_to_vector_db",
                    "namespace": namespace,
                    "vector_data": [{
                        "id": vector_id,
                        "values": vector_embed,
                        "metadata": {"original_text": text},
                    }],
                }
        
                kafka_producer.produce(
                    topic="vector.add_to_vector_db",
                    value=json.dumps(message).encode("utf-8"),
                )
                
                kafka_producer.flush()
                
                count += 1
        
            return namespace
    
        except Exception:
            return False

    def convert_query_to_vector_embed(self, query: str) -> list[float]:
        response = self.openai.embeddings.create(
            model="text-embedding-3-small",
            input=query,
        )
    
        return response.data[0].embedding

    def query_from_vector_db(self, vector_query: list[float], namespace: str) -> list[str] | bool:
        try:
            results = PC_INDEX.query(
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
    
        except Exception:
            return False

    def delete_from_vector_db(self, namespace: str) -> None:
        message = {
            "operation": "delete_from_vector_db",
            "namespace": namespace,
        }
    
        kafka_producer.produce(
            topic="vector.delete_from_vector_db",
            value=json.dumps(message).encode("utf-8"),
        )
    
        kafka_producer.flush()
