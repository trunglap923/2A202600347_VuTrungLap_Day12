import httpx
from openai import OpenAI
from ..config import settings
import logging

logger = logging.getLogger("agent")

# Khởi tạo client OpenAI với http_client trần để tránh lỗi proxy trên Windows/Docker
client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
    http_client=httpx.Client(proxies={})
)

def get_completion(messages: list) -> str:
    """
    Gọi OpenAI API để lấy câu trả lời.
    Messages là list các dict {"role": "...", "content": "..."}
    """
    try:
        if settings.OPENAI_API_KEY == "your-api-key-here":
            return "⚠️ OpenAI API Key chưa được cài đặt. Vui lòng kiểm tra file .env"

        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI API Error: {e}")
        return f"❌ Lỗi khi gọi OpenAI: {str(e)}"
