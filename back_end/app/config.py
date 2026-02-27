from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "PCB缺陷检测系统"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True
    
    DATABASE_URL: str = "sqlite:///./database.db"
    
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    UPLOAD_DIR: str = "./images"
    RESULTS_DIR: str = "./static/results"
    IMAGES_RESULTS_DIR: str = "./static/results/images"
    JSON_RESULTS_DIR: str = "./static/results/jsons"
    
    CORS_ORIGINS: list[str] = ["http://localhost:8080", "http://localhost:5173", "http://127.0.0.1:8080", "http://127.0.0.1:5173"]
    
    SMTP_SERVER: Optional[str] = None
    SMTP_PORT: int = 465
    SMTP_EMAIL: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    DEEPSEEK_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
