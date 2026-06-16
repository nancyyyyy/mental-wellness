from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..db.base import get_db
from ..services.knowledge_service import KnowledgeService
from pydantic import BaseModel

router = APIRouter()
knowledge_service = KnowledgeService()

class PracticeResponse(BaseModel):
    title: str
    why_it_helps: str
    steps: List[str]
    duration: str
    expected_benefit: str
    reflection_question: Optional[str] = None

@router.get("/recommend", response_model=List[PracticeResponse])
async def recommend_practices(
    user_id: str,
    emotion: Optional[str] = Query(None, description="Current emotional state"),
    limit: int = Query(3, ge=1, le=6),
    db: Session = Depends(get_db)
):
    query = emotion or "emotional regulation and coping skills"
    
    knowledge_items = knowledge_service.retrieve(
        query=query,
        category="emotional_wellness",
        limit=limit * 2
    )
    
    practices = []
    
    for item in knowledge_items[:limit]:
        title = item.get("title", "Mindfulness Practice")
        explanation = item.get("detailed_explanation", "")
        steps = item.get("step_by_step_exercise", [])
        
        practice = PracticeResponse(
            title=title,
            why_it_helps=explanation[:280] + "..." if len(explanation) > 280 else explanation,
            steps=steps[:5] if steps else ["Practice mindfully for a few minutes."],
            duration="3-10 minutes",
            expected_benefit="Improved emotional regulation and reduced distress.",
            reflection_question="How do you feel after trying this?"
        )
        practices.append(practice)
    
    if not practices:
        practices.append(PracticeResponse(
            title="5-4-3-2-1 Grounding",
            why_it_helps="This technique helps bring your attention back to the present moment when feeling overwhelmed or anxious.",
            steps=[
                "Name 5 things you can see",
                "Name 4 things you can touch",
                "Name 3 things you can hear",
                "Name 2 things you can smell",
                "Name 1 thing you can taste"
            ],
            duration="2-5 minutes",
            expected_benefit="Reduced anxiety and increased sense of calm.",
            reflection_question="How does your body feel now compared to before?"
        ))
    
    return practices
