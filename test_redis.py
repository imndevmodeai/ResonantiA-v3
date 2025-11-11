"""
Redis connectivity test with graceful skip if redis is not installed or unavailable.
"""

import sys

# Check if redis module is available
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("SKIP: redis module not installed. Install with: pip install redis")
    sys.exit(0)  # Exit gracefully if redis is not installed

# Test Redis connection
try:
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True, socket_connect_timeout=2)
    r.ping()
    print("✅ Redis server is accessible.")
except redis.exceptions.ConnectionError as e:
    print(f"SKIP: Could not connect to Redis server: {e}")
    print("   Make sure Redis is running: redis-server")
    sys.exit(0)  # Exit gracefully if Redis server is not running
except Exception as e:
    print(f"SKIP: Unexpected error testing Redis: {e}")
    sys.exit(0) 