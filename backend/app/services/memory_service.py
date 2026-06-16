from typing import List, Dict

class MemoryService:
    def __init__(self):
        pass

    def retrieve_relevant_memories(self, user_id: str, limit: int = 6) -> List[Dict]:
        # Temporarily disabled - return empty to avoid DB crash
        # TODO: Re-enable when memories table is created
        return []

    def add_memory(self, user_id: str, memory_text: str, memory_type: str = "general"):
        pass

    def extract_and_store_memories(self, user_id: str, user_input: str, ai_response: str):
        pass
