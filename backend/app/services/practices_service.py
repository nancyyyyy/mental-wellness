from typing import List, Dict
from ..db.base import get_db
from ..db.models import Memory
from ..core.config import settings
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

class PracticesService:
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

    def get_personalized_practices(self, user_id: str, limit: int = 5) -> List[Dict]:
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
                return self._get_general_calming_practices()

            memory_text = "\n".join([f"- {m.memory_text} (type: {m.memory_type})" for m in memories])

            prompt = f"""You are an experienced therapist recommending practices.

User's recent memories:
{memory_text}

Based on the user's emotional state and patterns above, recommend 3-4 most relevant practices from the following categories:
- Calming / Nervous system regulation
- Grounding techniques
- Emotional awareness
- Self-compassion
- Anxiety relief

For each practice, return in this exact format:

Name: [Practice Name]
Why: [1-2 sentences explaining why this is relevant for the user]
How: [Simple 2-4 step instructions]
Benefit: [Expected benefit]

Only return the practices in the format above. Do not add extra commentary."""

            response = self.llm.invoke(prompt)
            raw = response.content

            practices = []
            blocks = raw.strip().split("\n\n")

            for block in blocks:
                lines = block.strip().split("\n")
                data = {}
                for line in lines:
                    if line.startswith("Name:"):
                        data["name"] = line.replace("Name:", "").strip()
                    elif line.startswith("Why:"):
                        data["why"] = line.replace("Why:", "").strip()
                    elif line.startswith("How:"):
                        data["how"] = line.replace("How:", "").strip()
                    elif line.startswith("Benefit:"):
                        data["benefit"] = line.replace("Benefit:", "").strip()

                if "name" in data:
                    practices.append({
                        "name": data.get("name", "Practice"),
                        "why": data.get("why", ""),
                        "how": data.get("how", ""),
                        "benefit": data.get("benefit", "")
                    })

            return practices[:limit]

        finally:
            db.close()

    def _get_general_calming_practices(self) -> List[Dict]:
        """Fallback general calming practices"""
        return [
            {
                "name": "Box Breathing",
                "why": "A simple technique to quickly calm the nervous system when feeling anxious or overwhelmed.",
                "how": "Inhale for 4 seconds → Hold for 4 seconds → Exhale for 4 seconds → Hold for 4 seconds. Repeat 4 times.",
                "benefit": "Reduces immediate anxiety and helps regain a sense of control."
            },
            {
                "name": "5-4-3-2-1 Grounding",
                "why": "Helps bring attention back to the present moment when the mind feels scattered or anxious.",
                "how": "Name 5 things you can see, 4 things you can touch, 3 things you can hear, 2 things you can smell, and 1 thing you can taste.",
                "benefit": "Quickly reduces racing thoughts and increases present-moment awareness."
            }
        ]
