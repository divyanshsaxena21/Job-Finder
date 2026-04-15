from pydantic_settings import BaseSettings
from pydantic import ConfigDict
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
    # Development: http://localhost:5173,http://localhost:3000
    # Production: https://your-vercel-domain.vercel.app,https://your-domain.com
    cors_origins: str = "http://localhost:5173,http://localhost:3000,https://*.vercel.app"
    
    # Environment
    environment: str = "development"
    
    # Limits
    daily_application_limit: int = 5
    
    model_config = ConfigDict(env_file=".env", case_sensitive=False)
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        origins = [origin.strip().rstrip('/') for origin in self.cors_origins.split(",") if origin.strip()]
        # In production, allow all vercel.app subdomains
        if any("*.vercel.app" in origin for origin in origins):
            # Keep the wildcard for now; Vercel domains will be handled
            pass
        return origins


settings = Settings()
