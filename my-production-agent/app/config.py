from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "Production AI Agent"
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "production"
    
    # Instance ID for Scaling visibility
    INSTANCE_ID: Optional[str] = None
    
    # Security
    AGENT_API_KEY: str = "secret-api-key"
    JWT_SECRET: str = "super-secret-jwt-key"
    ALGORITHM: str = "HS256"
    
    # Redis (Stateless Store & Rate Limiting)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # OpenAI
    OPENAI_API_KEY: str = "your-api-key-here"
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    # Rate Limiting & Quotas
    RATE_LIMIT_PER_MINUTE: int = 10
    MONTHLY_BUDGET_USD: float = 10.0
    
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

settings = Settings()

