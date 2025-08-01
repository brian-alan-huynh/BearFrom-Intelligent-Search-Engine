import os
from datetime import datetime
from dotenv import load_dotenv
from typing import Optional
import uuid

import redis

load_dotenv()

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=os.getenv("REDIS_PORT"),
    decode_responses=True,
    username="default",
    password=os.getenv("REDIS_USER_PASS"),
)

def add_new_session() -> str:
    session_id = str(uuid.uuid4())
    
    redis_client.hset(session_id, mapping={
        "user_id": -1,
        "last_pinecone_vector_namespace": "",
        "logged_out_search_history": [],
        "logged_out_theme": "light",
        "logged_out_safesearch": "moderate",
        "created_at": datetime.now(),
    })

    return session_id

def get_session(session_id: str) -> dict:
    return redis_client.hgetall(session_id)

def modify_session(
    session_id: str,
    updated_user_id: Optional[int] = None,
    updated_pinecone_vector_namespace: Optional[str] = None,
    new_query: Optional[str] = None,
    updated_theme: Optional[str] = None,
    updated_safesearch_mode: Optional[str] = None,
) -> bool:
    
    if updated_user_id:
        redis_client.hset(session_id, "user_id", updated_user_id)
    if updated_pinecone_vector_namespace:
        redis_client.hset(session_id, "last_pinecone_vector_namespace", updated_pinecone_vector_namespace)
    if new_query:
        redis_client.hset(
            session_id, 
            "logged_out_search_history", 
            redis_client.hgetall(session_id).logged_out_search_history.append(new_query)
        )
    if updated_theme:
        redis_client.hset(session_id, "logged_out_theme", updated_theme)
    if updated_safesearch_mode:
        redis_client.hset(session_id, "logged_out_safesearch", updated_safesearch_mode)
    
    return True
