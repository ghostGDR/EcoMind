import json
import os
from pydantic import BaseModel
from typing import Optional
import logging

logger = logging.getLogger(__name__)
CONFIG_FILE = "data/config.json"

class Settings(BaseModel):
    llm_provider: str = os.environ.get("LLM_PROVIDER", "ollama")
    llm_model: str = os.environ.get("LLM_MODEL", "Qwen3-Coder-30B-A3B-Instruct-4bit")
    llm_base_url: str = os.environ.get("LLM_BASE_URL", os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:8000"))
    llm_api_key: Optional[str] = os.environ.get("LLM_API_KEY", "local")
    wiki_path: str = os.environ.get("WIKI_PATH", "")

def load_settings() -> Settings:
    """Load settings from config file or environment variables"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                # Filter out keys that aren't in Settings model
                valid_data = {k: v for k, v in data.items() if k in Settings.__fields__}
                return Settings(**valid_data)
        except Exception as e:
            logger.error(f"Error loading config file: {e}")
    
    return Settings()

def save_settings(settings: Settings):
    """Save settings to config file"""
    try:
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            json.dump(settings.dict(), f, indent=4)
        logger.info(f"Settings saved to {CONFIG_FILE}")
    except Exception as e:
        logger.error(f"Error saving config file: {e}")
        raise
