from typing import List, Dict
from sqlalchemy.orm import Session
from ..db.base import get_db
from ..db.models import Memory as DBMemory

class MemoryService:
    def __init__(self):
        pass

    def retrieve_relevant_memories(self, user_id: int, limit: int = 8) -> List[Dict]:
        """Get recent memories for the user"""
        db = next(get_db())
        try:
            memories = (
                db.query(DBMemory)
                .filter(DBMemory.user_id == user_id)
                .order_by(DBMemory.created_at.desc())
                .limit(limit)
                .all()
            )
            return [
                {
                    "id": m.id,
                    "text": m.memory_text,
                    "type": m.memory_type,
                    "timestamp": m.created_at.isoformat() if m.created_at else None
                }
                for m in memories
            ]
        finally:
            db.close()

    def add_memory(self, user_id: int, memory_text: str, memory_type: str = "general"):
        """Store memory in database"""
        if not memory_text or len(memory_text.strip()) < 10:
            return

        db = next(get_db())
        try:
            new_memory = DBMemory(
                user_id=user_id,
                memory_text=memory_text.strip(),
                memory_type=memory_type
            )
            db.add(new_memory)
            db.commit()
        finally:
            db.close()

    def extract_and_store_memories(self, user_id: int, user_input: str, ai_response: str):
        """
        Improved memory extraction with better categorization.
        This can later be replaced with LLM-based extraction for higher quality.
        """
        text_lower = user_input.lower()

        # 1. Emotional state
        emotion_keywords = ["i feel", "i'm feeling", "i am feeling", "makes me feel", 
                           "i've been feeling", "feeling very"]
        for keyword in emotion_keywords:
            if keyword in text_lower and len(user_input) > 15:
                self.add_memory(user_id, user_input, memory_type="emotion")
                break

        # 2. Triggers / Events
        trigger_phrases = ["because", "when that happened", "after", "it started when", 
                          "triggered by", "happened because"]
        for phrase in trigger_phrases:
            if phrase in text_lower and len(user_input) > 20:
                self.add_memory(user_id, user_input, memory_type="trigger")
                break

        # 3. Recurring patterns
        pattern_keywords = ["always", "never", "every time", "again and again", 
                           "keeps happening", "this happens whenever"]
        for keyword in pattern_keywords:
            if keyword in text_lower:
                self.add_memory(user_id, user_input, memory_type="pattern")
                break

        # 4. Needs / Wants
        need_keywords = ["i need", "i want", "i wish", "what i really need", 
                        "i just want to feel"]
        for keyword in need_keywords:
            if keyword in text_lower and len(user_input) > 12:
                self.add_memory(user_id, user_input, memory_type="need")
                break

        # 5. Self-talk / Beliefs
        belief_keywords = ["i think i'm", "i always tell myself", "deep down i feel", 
                          "i believe that", "part of me thinks"]
        for keyword in belief_keywords:
            if keyword in text_lower and len(user_input) > 18:
                self.add_memory(user_id, user_input, memory_type="belief")
                break
