from typing import List, Dict
from sqlalchemy.orm import Session
from ..db.base import get_db
from ..db.models import Memory as DBMemory
from datetime import datetime

class MemoryService:
    def __init__(self):
        pass

    def retrieve_relevant_memories(self, user_id: int, current_input: str = "", limit: int = 6) -> List[Dict]:
        """Retrieve recent memories for a user from PostgreSQL"""
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
        """Store a new memory in PostgreSQL"""
        if not memory_text or len(memory_text.strip()) < 8:
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
        """Simple rule-based memory extraction"""
        text = user_input.lower()

        # Store emotional expressions
        emotional_keywords = ["i feel", "i am feeling", "i'm feeling", "makes me feel"]
        for keyword in emotional_keywords:
            if keyword in text and len(user_input) > 12:
                self.add_memory(user_id, user_input, memory_type="emotion")
                break

        # Store triggers / events
        trigger_keywords = ["because", "when", "after", "happened when"]
        for keyword in trigger_keywords:
            if keyword in text and len(user_input) > 15:
                self.add_memory(user_id, user_input, memory_type="trigger")
                break

        # Store recurring patterns
        if any(word in text for word in ["always", "never", "every time", "again"]):
            self.add_memory(user_id, user_input, memory_type="pattern")
