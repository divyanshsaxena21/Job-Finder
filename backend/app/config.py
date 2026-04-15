from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    # Database
    mongodb_url: str
    db_name: str = "job_finder"
    
    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 24
    
    # Groq AI
    groq_api_key: str
    
    # Telegram
    telegram_bot_token: str
    
    # URLs
    backend_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:5173"
    
    # CORS - comma-separated list of allowed origins
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    
    # Environment
    environment: str = "development"
    
    # Limits
    daily_application_limit: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.cors_origins.split(",")]


settings = Settings()
