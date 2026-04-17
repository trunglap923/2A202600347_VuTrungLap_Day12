from fastapi import Header, HTTPException, Depends
from .config import settings
import jwt
from datetime import datetime, timezone

def verify_api_key(x_api_key: str = Header(None)):
    """Xác thực qua API Key truyền thống."""
    if x_api_key != settings.AGENT_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return "admin-user"  # Trả về user_id mặc định cho API Key

def verify_jwt_token(authorization: str = Header(None)):
    """Xác thực qua JWT Token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token missing subject")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(
    x_api_key: str | None = Header(default=None),
    authorization: str | None = Header(default=None)
):
    """Hỗ trợ đồng thời cả API Key và JWT Bearer Token."""
    # 1. Kiểm tra JWT Bearer Token (Authorization header)
    if authorization and authorization.startswith("Bearer "):
        try:
            return verify_jwt_token(authorization)
        except HTTPException:
            # Nếu JWT sai, ta có thể thử API Key bên dưới hoặc báo lỗi luôn
            raise
            
    # 2. Kiểm tra API Key (X-API-Key header)
    if x_api_key:
        if x_api_key == settings.AGENT_API_KEY:
            return "admin-api-user"
        raise HTTPException(status_code=401, detail="Invalid API Key")
        
    raise HTTPException(status_code=401, detail="Authentication required (X-API-Key or Bearer Token)")
