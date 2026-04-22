from fastapi import APIRouter, HTTPException
from src.api.config import Settings, load_settings, save_settings
import src.api.dependencies as deps
import logging

router = APIRouter(prefix="/api/config", tags=["config"])
logger = logging.getLogger(__name__)

@router.get("/")
async def get_config():
    """Get current system configuration"""
    return load_settings()

@router.post("/")
async def update_config(settings: Settings):
    """Update system configuration and reset internal components"""
    try:
        save_settings(settings)
        # Reset dependencies so they re-initialize with new config
        deps.reset_dependencies()
        return {"status": "success", "message": "Settings updated and components reset"}
    except Exception as e:
        logger.error(f"Failed to update config: {e}")
        raise HTTPException(status_code=500, detail=str(e))
