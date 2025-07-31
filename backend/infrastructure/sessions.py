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

# After user logs in:
#   Search history, theme, and safesearch data is recorded in AWS RDS
#   user_id is updated in Redis from -1 to the assigned user_id
def add_new_session() -> str:
    session_id = str(uuid.uuid4())
    
    redis_client.hset(session_id, mapping={
        "user_id": -1,
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
    user_id: Optional[int] = None,
    new_query: Optional[str] = None,
    theme: Optional[str] = None,
    safesearch: Optional[str] = None,
) -> bool:
    
    if user_id:
        redis_client.hset(session_id, "user_id", user_id)
    if new_query:
        redis_client.hset(
            session_id, 
            "logged_out_search_history", 
            redis_client.hgetall(session_id).logged_out_search_history.append(new_query)
        )
    if theme:
        redis_client.hset(session_id, "logged_out_theme", theme)
    if safesearch:
        redis_client.hset(session_id, "logged_out_safesearch", safesearch)
    
    return True
