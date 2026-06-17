from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict
from ..services.insights_service import InsightsService
from ..db.base import get_db
from sqlalchemy.orm import Session

router = APIRouter()
insights_service = InsightsService()

@router.get("/", response_model=List[Dict])
def get_insights(user_id: str, limit: int = 20, db: Session = Depends(get_db)):
    """Get stored insights for a user"""
    try:
        insights = insights_service.get_insights_for_user(user_id, limit=limit)
        return insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate", response_model=List[Dict])
def generate_insights(user_id: str):
    """Generate new insights for the user based on their memory"""
    try:
        new_insights = insights_service.generate_basic_insights(user_id)
        
        saved = []
        for ins in new_insights:
            saved_insight = insights_service.save_insight(
                user_id=user_id,
                title=ins["title"],
                explanation=ins["explanation"],
                insight_type=ins.get("insight_type", "general"),
                confidence=ins.get("confidence", 65)
            )
            saved.append({
                "id": saved_insight.id,
                "title": saved_insight.title,
                "explanation": saved_insight.explanation,
                "insight_type": saved_insight.insight_type,
                "confidence": saved_insight.confidence
            })
        
        return saved
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
