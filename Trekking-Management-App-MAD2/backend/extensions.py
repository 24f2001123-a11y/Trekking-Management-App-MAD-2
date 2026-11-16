#connectimg redis 

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import redis

# Create the database object
db = SQLAlchemy()

# Create the login manager object
login_manager = LoginManager()

import redis

# Create Redis connection
redis_client = redis.Redis(
    host="127.0.0.1",
    port=6379,
    db=0,
    decode_responses=True,
    socket_connect_timeout=0.2,
    socket_timeout=0.2,)




#   Check Redis connection once when Flask starts
redis_available = False

try:
    redis_client.ping()
    redis_available = True
except redis.RedisError:
    redis_available = False


    #disable Redis if connection fails
def disable_redis():
    global redis_available
    redis_available = False

#clear available trek cache
def clear_trek_cache():
    if not redis_available:
        return
    try:
        redis_client.delete("available_treks")

    except redis.RedisError:
        disable_redis()


   #CLEARING available trek cache
def clear_trek_cache():

    try:
        redis_client.delete("available_treks")

    except redis.RedisError:
        pass