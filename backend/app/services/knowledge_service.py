"""
Knowledge retrieval service — grounded RAG over the structured knowledge base.

Uses OpenAI embeddings + Qdrant vector search. Entries are ingested by
scripts/ingest_knowledge_base.py into the "mental_wellness_kb" collection.
"""
import os
from typing import List, Dict, Optional

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from openai import OpenAI

from ..core.config import settings

COLLECTION_NAME = "mental_wellness_kb"
EMBEDDING_MODEL = "text-embedding-3-small"  # 1536 dims, cheap and good
EMBEDDING_DIM = 1536


class KnowledgeService:
    def __init__(self):
        self._qdrant: Optional[QdrantClient] = None
        self._openai: Optional[OpenAI] = None

    # Lazy init so the app can boot even if Qdrant is momentarily down
    @property
    def qdrant(self) -> QdrantClient:
        if self._qdrant is None:
            url = os.getenv("QDRANT_URL", "http://localhost:6333")
            api_key = os.getenv("QDRANT_API_KEY")
            self._qdrant = QdrantClient(url=url, api_key=api_key)
        return self._qdrant

    @property
    def openai(self) -> OpenAI:
        if self._openai is None:
            self._openai = OpenAI(api_key=settings.OPENAI_API_KEY)
        return self._openai

    def embed(self, text: str) -> List[float]:
        resp = self.openai.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text,
        )
        return resp.data[0].embedding

    def ensure_collection(self):
        collections = {c.name for c in self.qdrant.get_collections().collections}
        if COLLECTION_NAME not in collections:
            self.qdrant.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=qmodels.VectorParams(
                    size=EMBEDDING_DIM,
                    distance=qmodels.Distance.COSINE,
                ),
            )

    def retrieve(
        self,
        query: str,
        category: Optional[str] = None,
        doc_type: Optional[str] = None,   # "technique" | "high_distress" | "insight_pattern"
        limit: int = 5,
        score_threshold: float = 0.25,
    ) -> List[Dict]:
        """
        Semantic search over the knowledge base.
        Optionally filter by category and/or doc_type payload fields.
        Returns normalized KB entry dicts (stored as payload).
        """
        query_vector = self.embed(query)

        must = []
        if category:
            must.append(
                qmodels.FieldCondition(
                    key="category",
                    match=qmodels.MatchValue(value=category),
                )
            )
        if doc_type:
            must.append(
                qmodels.FieldCondition(
                    key="doc_type",
                    match=qmodels.MatchValue(value=doc_type),
                )
            )

        response = self.qdrant.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            query_filter=qmodels.Filter(must=must) if must else None,
            limit=limit,
            score_threshold=score_threshold,
        )

        return [{**hit.payload, "score": hit.score} for hit in response.points]
