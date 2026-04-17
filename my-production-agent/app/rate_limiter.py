import time
import redis
from fastapi import HTTPException
from .config import settings

# Khởi tạo Redis client
r = redis.from_url(settings.REDIS_URL, decode_responses=True)

def check_rate_limit(user_id: str):
    """
    Sliding window rate limiter bằng Redis.
    Hạn mức: 10 req/phút.
    """
    now = time.time()
    key = f"rate_limit:{user_id}"
    
    try:
        # Pipeline để thực hiện các lệnh atomic
        pipe = r.pipeline()
        # Xóa các request cũ hơn 1 phút
        pipe.zremrangebyscore(key, 0, now - 60)
        # Đếm số request trong 1 phút qua
        pipe.zcard(key)
        # Thêm request hiện tại
        pipe.zadd(key, {str(now): now})
        # Set expire cho key để tự dọn dẹp
        pipe.expire(key, 60)
        
        results = pipe.execute()
        request_count = results[1]
        
        if request_count >= settings.RATE_LIMIT_PER_MINUTE:
            raise HTTPException(
                status_code=429, 
                detail=f"Rate limit exceeded. Max {settings.RATE_LIMIT_PER_MINUTE} req/min."
            )
            
    except redis.ConnectionError:
        # Fallback nếu Redis sập (tạm thời cho qua hoặc chặn tùy policy)
        print("⚠️ Redis connection error in rate limiter")
        return
