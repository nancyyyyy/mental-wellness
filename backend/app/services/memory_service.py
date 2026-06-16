from typing import List, Dict
import redis
import json
from datetime import datetime
from ..core.config import settings

class MemoryService:
    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
        self.memory_key_prefix = "user_memory:"

    def _get_key(self, user_id: str) -> str:
        return f"{self.memory_key_prefix}{user_id}"

    def retrieve_relevant_memories(self, user_id: str, current_input: str, limit: int = 5) -> List[Dict]:
        """
        Retrieve relevant memories for the current conversation.
        For now, returns recent memories. Can be upgraded to semantic search later.
        """
        key = self._get_key(user_id)
        memories_json = self.redis.get(key)
        
        if not memories_json:
            return []
        
        try:
            memories = json.loads(memories_json)
            # Return the most recent memories (can be improved with semantic search)
            return memories[-limit:] if len(memories) > limit else memories
        except:
            return []

    def add_memory(self, user_id: str, memory_text: str, memory_type: str = "general"):
        """
        Store a new memory. Only stores meaningful information.
        """
        if not memory_text or len(memory_text.strip()) < 10:
            return
            
        key = self._get_key(user_id)
        memories_json = self.redis.get(key)
        
        memories = []
        if memories_json:
            try:
                memories = json.loads(memories_json)
            except:
                memories = []
        
        new_memory = {
            "text": memory_text.strip(),
            "type": memory_type,
            "timestamp": datetime.now().isoformat()
        }
        
        memories.append(new_memory)
        
        # Keep only last 50 memories to avoid unlimited growth
        if len(memories) > 50:
            memories = memories[-50:]
        
        self.redis.set(key, json.dumps(memories))

    def extract_and_store_memories(self, user_id: str, user_input: str, ai_response: str):
        """
        Simple memory extraction. In production, this can be replaced with an LLM call.
        """
        # Store significant user statements
        significant_keywords = ["i feel", "i am", "my", "i have", "last time", "remember when"]
        
        user_lower = user_input.lower()
        
        for keyword in significant_keywords:
            if keyword in user_lower and len(user_input) > 15:
                self.add_memory(user_id, user_input, memory_type="user_statement")
                break
        
        # Store emotional patterns
        emotional_words = ["anxious", "sad", "overwhelmed", "happy", "frustrated", "lonely", "hopeful"]
        for word in emotional_words:
            if word in user_lower:
                self.add_memory(user_id, f"User expressed feeling {word}", memory_type="emotion")
                break
