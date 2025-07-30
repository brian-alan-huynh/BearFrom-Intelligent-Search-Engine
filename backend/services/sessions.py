import redis
import os

from dotenv import load_dotenv

load_dotenv()

# Stores the user.id as soon as create_user() is called and the search history and user preferences for users that haven't logged in
# When the user creates an account, the user row is returned with the user_id. store this returned user_id in redis. to access redis, look into the cookie and fetch the session id
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=os.getenv("REDIS_PORT"),
    decode_responses=True,
    username="default",
    password=os.getenv("REDIS_USER_PASS"),
)
