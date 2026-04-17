import redis
from fastapi import HTTPException
from .config import settings

r = redis.from_url(settings.REDIS_URL, decode_responses=True)

def check_budget(user_id: str, estimated_cost: float = 0.01):
    """
    Theo dõi chi phí sử dụng theo tháng trong Redis.
    """
    from datetime import datetime
    month_key = f"budget:{user_id}:{datetime.now().strftime('%Y-%m')}"
    
    try:
        # Lấy chi phí hiện tại
        current_cost = float(r.get(month_key) or 0.0)
        
        # Kiểm tra nếu vượt hạn mức
        if current_cost + estimated_cost > settings.MONTHLY_BUDGET_USD:
            raise HTTPException(
                status_code=402, 
                detail=f"Monthly budget exceeded (${settings.MONTHLY_BUDGET_USD}). Contact admin."
            )
        
        # Cập nhật chi phí (Atomic increment)
        # Redis không có trực tiếp float incr, dùng Lua script hoặc GET/SET cẩn thận
        # Ở đây dùng GET/SET đơn giản vì budget check không cần cực kỳ high-concurrency
        new_cost = current_cost + estimated_cost
        r.set(month_key, new_cost)
        # Hết tháng tự xóa (31 ngày)
        r.expire(month_key, 31 * 24 * 3600)
        
    except redis.ConnectionError:
        print("⚠️ Redis connection error in cost guard")
        return
