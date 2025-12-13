"""配置管理模块"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""
    
    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4"
    
    # Cognee
    cognee_api_url: str = "http://localhost:8000"
    cognee_api_token: Optional[str] = None
    
    # Memobase
    memobase_project_url: str = "http://localhost:8019"
    memobase_api_key: str = "secret"
    
    # Mem0
    mem0_api_url: str = "http://localhost:8888"
    mem0_api_key: Optional[str] = None
    
    # 应用配置
    app_host: str = "0.0.0.0"
    app_port: int = 8080
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

