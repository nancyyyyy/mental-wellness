import json
from typing import List, Dict
from pydantic import BaseModel
from ..db.base import get_db
from ..db.models import Memory
from ..core.config import settings
from ..services.knowledge_service import KnowledgeService
from langchain_openai import ChatOpenAI

DEFAULT_QUERY = "general calming grounding self-soothing techniques for everyday stress"


class PracticeRecommendation(BaseModel):
    name: str
    why: str
    how: str
    benefit: str


class PracticeList(BaseModel):
    practices: List[PracticeRecommendation]


class PracticesService:
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

    def _recent_memory_query(self, user_id: str) -> str:
        db = next(get_db())
        try:
            memories = (
                db.query(Memory)
                .filter(Memory.user_id == user_id)
                .order_by(Memory.created_at.desc())
                .limit(10)
                .all()
            )
            if not memories:
                return DEFAULT_QUERY
            return "; ".join(m.memory_text for m in memories)
        finally:
            db.close()

    def get_personalized_practices(self, user_id: str, limit: int = 5) -> List[Dict]:
        query = self._recent_memory_query(user_id)
        retrieved = self.knowledge_service.retrieve(
            query=query, doc_type="technique", limit=max(limit, 5)
        )

        if not retrieved:
            return []

        kb_context = "\n\n".join(
            f"**{item.get('title', '')}**\n"
            f"{item.get('body', '')}\n"
            f"Steps: {' | '.join(item.get('guidance', [])[:6])}"
            for item in retrieved
        )

        prompt = f"""You are an experienced, warm companion recommending self-help practices.

Knowledge base entries retrieved as relevant to this user right now:
{kb_context}

Based only on the material above, select and adapt {min(limit, len(retrieved))} of the most relevant practices for this user.
For each, write:
- name: the practice's name
- why: 1-2 sentences on why it's relevant right now
- how: simple 2-4 step instructions, adapted from the knowledge base guidance
- benefit: the expected benefit

Ground everything in the retrieved material above. Do not invent techniques that aren't represented there."""

        practices = self._generate_structured(prompt)
        return [p.model_dump() for p in practices[:limit]]

    def _generate_structured(self, prompt: str) -> List[PracticeRecommendation]:
        if settings.LLM_PROVIDER == "openai":
            structured_llm = self.llm.with_structured_output(PracticeList)
            result: PracticeList = structured_llm.invoke(prompt)
            return result.practices

        # Ollama fallback: no reliable structured-output/function-calling support
        raw = self.llm.invoke(
            prompt + "\n\nRespond with ONLY a JSON object: "
            '{"practices": [{"name": "...", "why": "...", "how": "...", "benefit": "..."}]}'
        ).content
        raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        try:
            data = json.loads(raw)
            return PracticeList.model_validate(data).practices
        except Exception:
            return []
