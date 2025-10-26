import redis

try:
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    r.ping()
    print("Redis server is accessible.")
except redis.exceptions.ConnectionError as e:
    print(f"Could not connect to Redis: {e}") 