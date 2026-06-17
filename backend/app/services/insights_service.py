from typing import List, Dict
from sqlalchemy.orm import Session
from ..db.base import get_db
from ..db.models import Memory, Insight
from datetime import datetime, timedelta

class InsightsService:
    def __init__(self):
        pass

    def generate_basic_insights(self, user_id: str, limit: int = 5) -> List[Dict]:
        """
        Generate simple insights from memory data.
        This is a starting point. Can be made much smarter later.
        """
        db = next(get_db())
        try:
            memories = (
                db.query(Memory)
                .filter(Memory.user_id == user_id)
                .order_by(Memory.created_at.desc())
                .limit(30)
                .all()
            )

            if not memories:
                return []

            insights = []

            type_count = {}
            for mem in memories:
                t = mem.memory_type or "general"
                type_count[t] = type_count.get(t, 0) + 1

            if type_count:
                most_common_type = max(type_count, key=type_count.get)
                if type_count[most_common_type] >= 3:
                    insights.append({
                        "title": f"Frequent {most_common_type.capitalize()} Memories",
                        "explanation": f"You have recorded {type_count[most_common_type]} memories related to {most_common_type}. This may indicate it's an important area for you right now.",
                        "insight_type": "pattern",
                        "confidence": 65,
                        "related_themes": most_common_type
                    })

            recent_emotions = [m for m in memories if m.memory_type == "emotion"][:5]
            if len(recent_emotions) >= 2:
                insights.append({
                    "title": "Recent Emotional Activity",
                    "explanation": f"You've shared several emotional experiences recently. Paying attention to these patterns can help build better self-awareness.",
                    "insight_type": "growth",
                    "confidence": 60,
                    "related_themes": "emotion"
                })

            return insights[:limit]

        finally:
            db.close()

    def save_insight(self, user_id: str, title: str, explanation: str, insight_type: str = "general", confidence: int = 70):
        db = next(get_db())
        try:
            new_insight = Insight(
                user_id=user_id,
                title=title,
                explanation=explanation,
                insight_type=insight_type,
                confidence=confidence
            )
            db.add(new_insight)
            db.commit()
            return new_insight
        finally:
            db.close()

    def get_insights_for_user(self, user_id: str, limit: int = 20) -> List[Dict]:
        db = next(get_db())
        try:
            insights = (
                db.query(Insight)
                .filter(Insight.user_id == user_id)
                .order_by(Insight.created_at.desc())
                .limit(limit)
                .all()
            )
            return [
                {
                    "id": i.id,
                    "title": i.title,
                    "explanation": i.explanation,
                    "insight_type": i.insight_type,
                    "confidence": i.confidence,
                    "created_at": i.created_at.isoformat() if i.created_at else None
                }
                for i in insights
            ]
        finally:
            db.close()
