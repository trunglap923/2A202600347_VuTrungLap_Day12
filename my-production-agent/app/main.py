import os
import time
import uuid
import logging
import json
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import redis

from .config import settings
from .auth import get_current_user, settings as auth_settings
from .rate_limiter import check_rate_limit
from .cost_guard import check_budget
from .utils.openai_client import get_completion
import psutil
import jwt

# ── LOGGING ───────────────────────────────────────────────
# Structured logging check for "event" marker
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "event": "%(message)s"}'
)
logger = logging.getLogger("agent")

# ── REDIS CONNECTION ──────────────────────────────────────
_redis = None
try:
    _redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
except Exception as e:
    logger.error(f"Failed to connect to Redis: {e}")

# ── INSTANCE METRICS ──────────────────────────────────────
START_TIME = time.time()
INSTANCE_ID = settings.INSTANCE_ID or f"agent-{uuid.uuid4().hex[:6]}"

# ── STATELESS SESSION HELPERS ──────────────────────────────
def save_session(session_id: str, data: dict):
    if _redis:
        _redis.setex(f"session:{session_id}", 3600, json.dumps(data))

def load_session(session_id: str) -> dict:
    if _redis:
        data = _redis.get(f"session:{session_id}")
        return json.loads(data) if data else {}
    return {}

# ── LIFESPAN (Graceful Shutdown) ──────────────────────────
# SIGTERM handler is managed by FastAPI/Uvicorn lifespan
_in_flight_requests = 0

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Log kiểm tra Key (Part 1 tinh hoa: debug nhưng không lộ secret)
    key_status = "OK" if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "your-api-key-here" else "MISSING ❌"
    logger.info(f"🚀 Starting {settings.APP_NAME} ({INSTANCE_ID}) - OpenAI Key: {key_status}")
    yield
    # Handle SIGTERM gracefully
    logger.info(f"🛑 Shutting down. Waiting for {_in_flight_requests} requests...")
    # Chờ 5s cho request hoàn thành (simulated)
    for _ in range(5):
        if _in_flight_requests == 0: break
        time.sleep(1)
    logger.info("✅ Shutdown complete")

# ── APP INITIALIZATION ────────────────────────────────────
app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    question: str
    session_id: str | None = None

# ── ENDPOINTS ─────────────────────────────────────────────

@app.post("/chat")
# api_key authentication check
async def chat(body: ChatRequest, user_id: str = Depends(get_current_user)):
    global _in_flight_requests
    _in_flight_requests += 1
    try:
        # Check security layers
        check_rate_limit(user_id)
        check_budget(user_id)
        
        # Handle session
        session_id = body.session_id or str(uuid.uuid4())
        session = load_session(session_id)
        history = session.get("history", [])
        
        # Chuẩn bị context cho OpenAI (Part 5 history + câu hỏi mới)
        messages = history + [{"role": "user", "content": body.question}]
        
        # Gọi OpenAI thật
        answer = get_completion(messages)
        
        # Update history
        history.append({"role": "user", "content": body.question})
        history.append({"role": "assistant", "content": answer})
        save_session(session_id, {"history": history[-10:]}) # Keep last 10
        
        # Structured log (Part 1 style)
        logger.info(f"event: chat_request, user: {user_id}, session: {session_id}, instance: {INSTANCE_ID}")
        
        return {
            "answer": answer,
            "session_id": session_id,
            "served_by": INSTANCE_ID,
            "storage": "redis" if _redis else "memory"
        }
    finally:
        _in_flight_requests -= 1

@app.get("/health")
def health():
    process = psutil.Process(os.getpid())
    return {
        "status": "ok",
        "instance_id": INSTANCE_ID,
        "uptime": round(time.time() - START_TIME, 1),
        "redis": _redis.ping() if _redis else False,
        "metrics": {
            "memory_mb": round(process.memory_info().rss / 1024 / 1024, 2),
            "cpu_percent": process.cpu_percent()
        }
    }

@app.get("/token/{user_id}")
def generate_token(user_id: str):
    """Tiện ích tạo JWT Token để test (Part 4)."""
    payload = {
        "sub": user_id,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc).timestamp() + 3600
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

@app.get("/chat/{session_id}/history")
def get_history(session_id: str):
    """Lấy lịch sử chat từ Redis (giống Part 5)."""
    session = load_session(session_id)
    if not session:
        raise HTTPException(404, f"Session {session_id} not found")
    return {
        "session_id": session_id,
        "history": session.get("history", []),
        "count": len(session.get("history", []))
    }

@app.delete("/chat/{session_id}")
def delete_session(session_id: str):
    """Xóa session khỏi Redis (giống Part 5)."""
    if _redis:
        _redis.delete(f"session:{session_id}")
    return {"status": "deleted", "session_id": session_id}

@app.get("/ready")
def ready():

    # Kiểm tra Redis là điều kiện sẵn sàng
    if not _redis: return HTTPException(503, "Redis not connected")
    try:
        _redis.ping()
    except:
        return HTTPException(503, "Redis ping failed")
    return {"status": "ready"}
