from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path
from typing import Optional

class Settings(BaseSettings):
    API_BASE_URL: str = "https://sf34-terminlister-prod-app.azurewebsites.net"
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432
    POSTGRES_HOST: str = "localhost"

    # MinIO settings
    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET: str = "hockey-images"
    MINIO_REGION: str = "us-east-1"
    MINIO_SECURE: bool = False  # Set to True for HTTPS

   # Claude API (add this now)
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # Environment detection
    ENVIRONMENT: str = "development"  # development, production, test
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT.lower() == "development"
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        extra= 'ignore'

@lru_cache()
def get_settings():
    return Settings()