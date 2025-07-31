import redis
import os

from dotenv import load_dotenv

load_dotenv()

# Stores the user.id as soon as create_user() is called and the search history and user preferences for users that haven't logged in
# When the user creates an account, the user row is returned with the user_id. store this returned user_id in redis. to access redis, look into the cookie and fetch the session id, then query redis to fetch the row that corresponds with that session_id, then fetch the user_id
# if the user logs out, delete all session data of the corresponding session_id from redis
# if user_id is not found in redis, the user is not logged in
# every 60 days, destroy the cookie and its session_id row from redis to force the user to log out again
# if the user isnt logged in and submits feedback, a developer response isn't needed and the user response sender will be anonymous
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=os.getenv("REDIS_PORT"),
    decode_responses=True,
    username="default",
    password=os.getenv("REDIS_USER_PASS"),
)
