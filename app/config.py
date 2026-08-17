from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field("Enterprise RAG Chatbot", env="APP_NAME")
    environment: str = Field("development", env="ENVIRONMENT")
    debug: bool = Field(True, env="DEBUG")

    api_host: str = Field("0.0.0.0", env="API_HOST")
    api_port: int = Field(8000, env="API_PORT")
    streamlit_port: int = Field(8501, env="STREAMLIT_PORT")

    log_level: str = Field("INFO", env="LOG_LEVEL")
    backend_base_url: str = Field("http://127.0.0.1:8000", env="BACKEND_BASE_URL")

    data_dir: Path = Field(Path("data"), env="DATA_DIR")
    vector_store_dir: Path = Field(Path("data/vectorstore"), env="VECTOR_STORE_DIR")

    openai_api_key: str | None = Field(default=None, env="OPENAI_API_KEY")

    supported_file_extensions: set[str] = Field(default_factory=lambda: {".pdf", ".docx", ".txt"}, env="SUPPORTED_FILE_EXTENSIONS")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


    embedding_provider: str = Field("openai", env="EMBEDDING_PROVIDER")
    embedding_model: str = Field("text-embedding-3-small", env="EMBEDDING_MODEL")
    embedding_batch_size: int = Field(100, env="EMBEDDING_BATCH_SIZE")
    embedding_max_retries: int = Field(3, env="EMBEDDING_MAX_RETRIES")
    vector_collection_name: str = Field("enterprise_docs", env="VECTOR_COLLECTION_NAME")
    retrieval_default_top_k: int = Field(5, env="RETRIEVAL_DEFAULT_TOP_K")
    retrieval_max_top_k: int = Field(20, env="RETRIEVAL_MAX_TOP_K")
    reindex_mode: str = Field("replace", env="REINDEX_MODE") 
    


@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()