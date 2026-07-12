import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """
    Central configuration for FinSight
    """

    # -------------------------------
    # API Keys
    # -------------------------------
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    HUGGINGFACE_API_KEY: str = os.getenv("HUGGINGFACE_API_KEY", "")

    # -------------------------------
    # Model Config
    # -------------------------------
    _LLM_PROVIDER_RAW: str = os.getenv("LLM_PROVIDER", "ollama")
    LLM_PROVIDER: str = _LLM_PROVIDER_RAW.strip().lower()  # "openai" or "ollama"
    LLM_MODEL: str = os.getenv("LLM_MODEL", "mistral" if LLM_PROVIDER == "ollama" else "gpt-4o-mini")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "nomic-embed-text" if LLM_PROVIDER == "ollama" else "text-embedding-3-small")

    # -------------------------------
    # File Paths
    # -------------------------------
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    RAW_DATA_DIR: str = os.path.join(DATA_DIR, "raw")
    PROCESSED_DATA_DIR: str = os.path.join(DATA_DIR, "processed")
    EMBEDDINGS_DIR: str = os.path.join(DATA_DIR, "embeddings")

    # -------------------------------
    # RAG Settings
    # -------------------------------
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", 1000))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", 200))
    TOP_K: int = int(os.getenv("TOP_K", 5))

    # -------------------------------
    # App Settings
    # -------------------------------
    APP_NAME: str = "FinSight"
    DEBUG: bool = os.getenv("DEBUG", "True") == "True"


# Create a global settings object
settings = Settings()