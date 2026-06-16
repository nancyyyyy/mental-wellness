from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost/mindcompanion"
    REDIS_URL: str = "redis://localhost:6379"
    QDRANT_URL: str = "http://localhost:6333"
    OPENAI_API_KEY: str = ""
    SECRET_KEY: str = "change-me"

    class Config:
        env_file = ".env"

settings = Settings()