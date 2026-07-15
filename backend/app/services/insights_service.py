import json
from typing import List, Dict
from pydantic import BaseModel
from ..db.base import get_db
from ..db.models import Memory, Insight
from ..core.config import settings
from ..services.knowledge_service import KnowledgeService
from langchain_openai import ChatOpenAI


class InsightItem(BaseModel):
    title: str
    explanation: str
    insight_type: str
    confidence: int


class InsightList(BaseModel):
    insights: List[InsightItem]


class InsightsService:
    def __init__(self):
        if settings.LLM_PROVIDER == "openai":
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
        self.knowledge_service = KnowledgeService()

    def generate_smart_insights(self, user_id: str, limit: int = 5) -> List[Dict]:
        """
        Generate high-quality insights using LLM + memory data, grounded in
        retrieved insight_pattern knowledge base material.
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

            retrieved = self.knowledge_service.retrieve(
                query=memory_text, doc_type="insight_pattern", limit=3
            )
            pattern_context = ""
            if retrieved:
                pattern_context = "\n\nRelevant psychological patterns from the knowledge base (use this observation-style language as a model for tone):\n"
                for item in retrieved:
                    pattern_context += f"\n**{item.get('title', '')}**\n{item.get('body', '')}\n"
                    if item.get("guidance"):
                        pattern_context += "Observation language: " + " | ".join(item["guidance"][:3]) + "\n"

            prompt = f"""You are an experienced therapist analyzing a user's emotional patterns from their conversation history.

Here are the user's recent memories:

{memory_text}
{pattern_context}

Based on the above, generate 2-4 meaningful, personalized insights.
Focus on:
- Recurring emotional patterns or triggers
- Behavioral tendencies
- Areas of growth or positive change
- Relationship dynamics (if visible)

Use gentle, therapist-style observation language (e.g. "It seems like...", "There appears to be a pattern of..."), consistent with the knowledge base material above when relevant.

For each insight, provide:
- title: a short, clear title
- explanation: 2-4 sentences explaining the insight with warmth and clarity
- insight_type: one of trigger / behavioral / growth / relationship / general
- confidence: an integer 60-90"""

            insights = self._generate_structured(prompt)
            return [i.model_dump() for i in insights[:limit]]

        finally:
            db.close()

    def _generate_structured(self, prompt: str) -> List[InsightItem]:
        if settings.LLM_PROVIDER == "openai":
            structured_llm = self.llm.with_structured_output(InsightList)
            result: InsightList = structured_llm.invoke(prompt)
            return result.insights

        raw = self.llm.invoke(
            prompt + "\n\nRespond with ONLY a JSON object: "
            '{"insights": [{"title": "...", "explanation": "...", "insight_type": "...", "confidence": 70}]}'
        ).content
        raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        try:
            data = json.loads(raw)
            return InsightList.model_validate(data).insights
        except Exception:
            return []

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
            db.refresh(new_insight)
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
