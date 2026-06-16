from pydantic_settings import BaseSettings
from typing import Literal

class Settings(BaseSettings):
    LLM_PROVIDER: Literal["groq", "openai", "ollama"] = "groq"
    
    # Groq (Free tier - recommended for testing)
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.1-8b-instant"   # or "llama-3.1-70b-versatile"
    
    # OpenAI (paid)
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    # Ollama (local)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1"
    
    # Database & others
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost/mindcompanion"
    REDIS_URL: str = "redis://localhost:6379"
    QDRANT_URL: str = "http://localhost:6333"
    SECRET_KEY: str = "change-me-in-production"

    class Config:
        env_file = ".env"

settings = Settings()