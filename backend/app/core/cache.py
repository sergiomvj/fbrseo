import redis
from typing import Optional, Any
import json
from app.config import settings

# Cliente Redis
redis_client = redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    encoding='utf-8'
)


class Cache:
    """
    Wrapper para operações de cache
    """
    
    @staticmethod
    def get(key: str) -> Optional[Any]:
        """Busca valor do cache"""
        try:
            value = redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    @staticmethod
    def set(key: str, value: Any, ttl: int = 300) -> bool:
        """
        Salva valor no cache
        ttl: time to live em segundos (default 5 minutos)
        """
        try:
            redis_client.setex(
                key,
                ttl,
                json.dumps(value)
            )
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    @staticmethod
    def delete(key: str) -> bool:
        """Remove valor do cache"""
        try:
            redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    @staticmethod
    def clear_pattern(pattern: str) -> int:
        """
        Remove todas as keys que correspondem ao pattern
        Ex: clear_pattern("api_key:*")
        """
        try:
            keys = redis_client.keys(pattern)
            if keys:
                return redis_client.delete(*keys)
            return 0
        except Exception as e:
            print(f"Cache clear pattern error: {e}")
            return 0


class RateLimiter:
    """
    Rate limiting usando Redis
    """
    
    @staticmethod
    def check_rate_limit(
        client_id: int,
        limit_per_minute: int,
        limit_per_day: int
    ) -> tuple[bool, dict]:
        """
        Verifica rate limits
        Returns: (allowed, info_dict)
        """
        from datetime import datetime
        
        now = datetime.utcnow()
        
        # Keys para rate limiting
        minute_key = f"rate_limit:client:{client_id}:minute:{now.strftime('%Y%m%d%H%M')}"
        day_key = f"rate_limit:client:{client_id}:day:{now.strftime('%Y%m%d')}"
        
        try:
            # Incrementa contadores
            minute_count = redis_client.incr(minute_key)
            day_count = redis_client.incr(day_key)
            
            # Define expiração
            if minute_count == 1:
                redis_client.expire(minute_key, 60)
            if day_count == 1:
                redis_client.expire(day_key, 86400)
            
            # Verifica limites
            allowed = True
            reason = None
            
            if minute_count > limit_per_minute:
                allowed = False
                reason = "minute_limit_exceeded"
            elif day_count > limit_per_day:
                allowed = False
                reason = "day_limit_exceeded"
            
            info = {
                "allowed": allowed,
                "reason": reason,
                "minute_count": minute_count,
                "minute_limit": limit_per_minute,
                "day_count": day_count,
                "day_limit": limit_per_day,
                "remaining_minute": max(0, limit_per_minute - minute_count),
                "remaining_day": max(0, limit_per_day - day_count)
            }
            
            return allowed, info
            
        except Exception as e:
            print(f"Rate limit error: {e}")
            # Em caso de erro no Redis, permite a requisição
            return True, {"allowed": True, "error": str(e)}
    
    @staticmethod
    def get_current_usage(client_id: int) -> dict:
        """Retorna uso atual do cliente"""
        from datetime import datetime
        
        now = datetime.utcnow()
        minute_key = f"rate_limit:client:{client_id}:minute:{now.strftime('%Y%m%d%H%M')}"
        day_key = f"rate_limit:client:{client_id}:day:{now.strftime('%Y%m%d')}"
        
        try:
            minute_count = redis_client.get(minute_key) or 0
            day_count = redis_client.get(day_key) or 0
            
            return {
                "minute_count": int(minute_count),
                "day_count": int(day_count)
            }
        except Exception as e:
            return {"error": str(e)}
