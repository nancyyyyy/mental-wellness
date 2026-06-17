from fastapi import APIRouter, HTTPException
from typing import List, Dict
from ..services.practices_service import PracticesService

router = APIRouter()
practices_service = PracticesService()

@router.get("/recommendations", response_model=List[Dict])
def get_personalized_practices(user_id: str, limit: int = 4):
    """Get personalized practice recommendations for the user"""
    try:
        practices = practices_service.get_personalized_practices(user_id, limit=limit)
        return practices
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
