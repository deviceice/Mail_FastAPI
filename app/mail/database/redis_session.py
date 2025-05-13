from fastapi import Request
from redis.asyncio import Redis


async def get_redis(request: Request) -> Redis:
    """
    Возвращает соединение Redis из пула для каждого запроса.
    Соединение автоматически возвращается в пул после завершения обработки запроса.
    """
    return Redis(connection_pool=request.app.state.redis_pool)
