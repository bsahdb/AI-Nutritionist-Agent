from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    # Pydantic v2 写法
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    APP_NAME: str = "AI营养师系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
     
    # APP_NAME: str = "AI营养师Agent"
    # APP_VERSION: str = "1.0.0"
    # DEBUG: bool = True
    
    DATABASE_URL: str = " "
    # LLM：用于饮食计划生成、AI营养师对话
    LLM_PROVIDER: str = "deepseek"
    LLM_API_KEY: str = "your-key"
    LLM_BASE_URL: str = "https://api.deepseek.com"
    LLM_MODEL: str = "deepseek-chat"

    # Embedding：用于知识库向量化，不建议用 DeepSeek
    EMBEDDING_PROVIDER: str = "local"
    LOCAL_EMBEDDING_MODEL: str = "BAAI/bge-small-zh-v1.5"

    # EMBEDDING_API_KEY: str = ""
    # EMBEDDING_BASE_URL: str = "https://api.openai.com/v1"
    # EMBEDDING_MODEL: str = "text-embedding-3-small"

    CHROMA_PERSIST_DIR: str = "./knowledge_base"
    CHROMA_COLLECTION_NAME: str = "nutrition_knowledge"
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    TOP_K: int = 5
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]

settings = Settings()
