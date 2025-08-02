import os
from datetime import datetime
from dotenv import load_dotenv
from typing import Optional
import uuid

import redis

load_dotenv()

class RedisSession:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST"),
            port=os.getenv("REDIS_PORT"),
            decode_responses=True,
            username="default",
            password=os.getenv("REDIS_USER_PASS"),
        )

    def add_new_session(self) -> str:
        session_id = str(uuid.uuid4())
        session_key = f"session:{session_id}"
        
        self.redis_client.hset(session_key, mapping={
            "user_id": -1,
            "last_pinecone_vector_namespace": "",
            "logged_out_search_history": [],
            "logged_out_theme": "light",
            "logged_out_safesearch": "moderate",
            "created_at": datetime.now(),
        })

        return session_key

    def get_session(self, session_key: str) -> dict:
        return self.redis_client.hgetall(session_key)

    def modify_session(
        self,
        session_key: str,
        updated_user_id: Optional[int] = None,
        updated_pinecone_vector_namespace: Optional[str] = None,
        new_query: Optional[str] = None,
        updated_theme: Optional[str] = None,
        updated_safesearch_mode: Optional[str] = None,
    ) -> None:
        
        if updated_user_id:
            self.redis_client.hset(session_key, "user_id", updated_user_id)
        if updated_pinecone_vector_namespace:
            self.redis_client.hset(session_key, "last_pinecone_vector_namespace", updated_pinecone_vector_namespace)
        if new_query:
            self.redis_client.hset(
                session_key, 
                "logged_out_search_history", 
                self.redis_client.hgetall(session_key)["logged_out_search_history"].append(new_query)
            )
        if updated_theme:
            self.redis_client.hset(session_key, "logged_out_theme", updated_theme)
        if updated_safesearch_mode:
            self.redis_client.hset(session_key, "logged_out_safesearch", updated_safesearch_mode)

    def delete_session(self, session_key: str) -> None:
        self.redis_client.delete(session_key)
