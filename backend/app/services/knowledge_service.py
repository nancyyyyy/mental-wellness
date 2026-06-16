from typing import List, Dict, Optional

class KnowledgeService:
    def __init__(self):
        pass

    def retrieve(
        self, 
        query: str, 
        category: Optional[str] = None, 
        limit: int = 5
    ) -> List[Dict]:
        """
        Temporary stub - returns empty list.
        We'll implement real retrieval later.
        """
        return []
