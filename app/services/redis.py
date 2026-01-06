import redis
from redis.exceptions import ConnectionError, TimeoutError
from contextlib import contextmanager
from typing import Optional

class RedisService:
    def __init__(self, host: str = "redis-server", port: int = 6379, db: int = 0):
        self.host = host
        self.port = port
        self.db = db
        self._connection: Optional[redis.Redis] = None
    
    def connect(self) -> bool:
        """Устанавливает соединение с Redis"""
        try:
            self._connection = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                socket_connect_timeout=5,
                decode_responses=True
            )
            self._connection.ping()
            print("Redis подключён!")
            return True
        except (ConnectionError, TimeoutError) as e:
            print(f"Не удалось подключиться к Redis: {e}")
            return False

    @property
    def connection(self) -> redis.Redis:
        if not self._connection:
            if not self.connect():
                raise ConnectionError("Redis connection not established")
        return self._connection

    @contextmanager
    def get_connection(self):
        try:
            yield self.connection
        except (ConnectionError, TimeoutError) as e:
            print(f"Redis connection error: {e}")
            raise

redis_service = RedisService()