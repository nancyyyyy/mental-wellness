from typing import List, Dict
from ..db.base import get_db
from ..db.models import Memory, Insight
from ..core.config import settings
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

class InsightsService:
    def __init__(self):
        if settings.LLM_PROVIDER == "groq":
            self.llm = ChatGroq(
                groq_api_key=settings.GROQ_API_KEY,
                model_name=settings.GROQ_MODEL,
                temperature=0.6,
            )
        elif settings.LLM_PROVIDER == "openai":
            self.llm = ChatOpenAI(
                openai_api_key=settings.OPENAI_API_KEY,
                model=settings.OPENAI_MODEL,
                temperature=0.6,
            )
        else:
            self.llm = ChatOpenAI(
                base_url=f"{settings.OLLAMA_BASE_URL}/v1",
                api_key="ollama",
                model=settings.OLLAMA_MODEL,
                temperature=0.6,
            )

    def generate_smart_insights(self, user_id: str, limit: int = 5) -> List[Dict]:
        """
        Generate high-quality insights using LLM + memory data.
        """
        db = next(get_db())
        try:
            memories = (
                db.query(Memory)
                .filter(Memory.user_id == user_id)
                .order_by(Memory.created_at.desc())
                .limit(25)
                .all()
            )

            if not memories:
                return []

            memory_text = "\n".join([f"- {m.memory_text} (type: {m.memory_type})" for m in memories])

            prompt = f"""You are an experienced therapist analyzing a user's emotional patterns from their conversation history.

Here are the user's recent memories:

{memory_text}

Based on the above, generate 2-4 meaningful, personalized insights. 
Focus on:
- Recurring emotional patterns or triggers
- Behavioral tendencies
- Areas of growth or positive change
- Relationship dynamics (if visible)

For each insight, return in this exact format:

Title: [Short, clear title]
Type: [trigger / behavioral / growth / relationship / general]
Explanation: [2-4 sentences explaining the insight with warmth and clarity]
Confidence: [60-90]

Only return the insights in the format above. Do not add extra text."""

            response = self.llm.invoke(prompt)
            raw = response.content

            insights = []
            blocks = raw.strip().split("\n\n")

            for block in blocks:
                lines = block.strip().split("\n")
                data = {}
                for line in lines:
                    if line.startswith("Title:"):
                        data["title"] = line.replace("Title:", "").strip()
                    elif line.startswith("Type:"):
                        data["insight_type"] = line.replace("Type:", "").strip().lower()
                    elif line.startswith("Explanation:"):
                        data["explanation"] = line.replace("Explanation:", "").strip()
                    elif line.startswith("Confidence:"):
                        try:
                            data["confidence"] = int(line.replace("Confidence:", "").strip())
                        except:
                            data["confidence"] = 70

                if "title" in data and "explanation" in data:
                    insights.append({
                        "title": data.get("title", "Personal Insight"),
                        "explanation": data.get("explanation", ""),
                        "insight_type": data.get("insight_type", "general"),
                        "confidence": data.get("confidence", 70)
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
