"""
Ingest ALL knowledge sources into Qdrant:

  1. knowledge_base/mental_wellness_knowledge_base.json   (list of technique entries)
  2. artifacts/knowledge_base/high_distress/*.json         (distress-support protocols)
  3. artifacts/knowledge_base/insight_generation/*.json    (pattern/insight docs)

Each source has a different schema; everything is normalized into a common
payload so retrieval and prompt-building work uniformly:

    id, doc_type, title, category, body, guidance (list[str]),
    example_response, severity, tags, source_file

Usage (from the backend/ directory, with .env populated):
    python -m scripts.ingest_knowledge_base

Safe to re-run: point IDs are deterministic (derived from file/entry ID),
so updated documents overwrite their previous versions.
"""
import json
import sys
import uuid
from pathlib import Path
from typing import Dict, List

from dotenv import load_dotenv

load_dotenv()

from qdrant_client.http import models as qmodels  # noqa: E402
from app.services.knowledge_service import (  # noqa: E402
    KnowledgeService,
    COLLECTION_NAME,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
MAIN_KB = REPO_ROOT / "knowledge_base" / "mental_wellness_knowledge_base.json"
HIGH_DISTRESS_DIR = REPO_ROOT / "artifacts" / "knowledge_base" / "high_distress"
INSIGHT_DIR = REPO_ROOT / "artifacts" / "knowledge_base" / "insight_generation"


# ---------------------------------------------------------------------------
# Normalizers — one per schema → common payload
# ---------------------------------------------------------------------------
def normalize_technique(entry: Dict, source: str) -> Dict:
    """Main KB schema: id/category/summary/detailed_explanation/steps/..."""
    return {
        "id": entry.get("id") or source,
        "doc_type": "technique",
        "title": entry.get("title", ""),
        "category": entry.get("category", ""),
        "body": "\n".join(
            p for p in [
                entry.get("summary", ""),
                entry.get("detailed_explanation", ""),
                f"When to use: {entry.get('when_to_use', '')}" if entry.get("when_to_use") else "",
                f"When NOT to use: {entry.get('when_not_to_use', '')}" if entry.get("when_not_to_use") else "",
            ] if p
        ),
        "guidance": entry.get("step_by_step_exercise", []),
        "example_response": entry.get("example_scenario", ""),
        "severity": entry.get("risk_level", ""),
        "tags": entry.get("keywords", []),
        "source_file": source,
    }


def normalize_high_distress(entry: Dict, source: str) -> Dict:
    """artifacts/high_distress schema: content/example_response/what_to_avoid."""
    guidance = []
    for item in entry.get("what_to_avoid", []):
        guidance.append(f"AVOID: {item}")
    return {
        "id": source,
        "doc_type": "high_distress",
        "title": entry.get("title", ""),
        "category": entry.get("category", "High Distress Support"),
        "body": entry.get("content", ""),
        "guidance": guidance,
        "example_response": entry.get("example_response", ""),
        "severity": entry.get("severity_level", "High"),
        "tags": entry.get("tags", []) + entry.get("emotional_state", []),
        "source_file": source,
    }


def normalize_insight(entry: Dict, source: str) -> Dict:
    """artifacts/insight_generation schema: description/observation_language."""
    obs = entry.get("observation_language", [])
    if isinstance(obs, str):
        obs = [obs]
    return {
        "id": source,
        "doc_type": "insight_pattern",
        "title": entry.get("title", ""),
        "category": entry.get("category", "Insight Generation"),
        "body": "\n".join(
            p for p in [
                entry.get("description", ""),
                "Underlying fears: " + ", ".join(entry.get("underlying_fears", []))
                if entry.get("underlying_fears") else "",
            ] if p
        ),
        "guidance": [f"Observation language: {o}" for o in obs],
        "example_response": "",
        "severity": "",
        "tags": entry.get("tags", []) + entry.get("common_emotions", []),
        "source_file": source,
    }


def doc_to_embed_text(doc: Dict) -> str:
    return "\n".join(
        p for p in [
            doc["title"],
            doc["category"],
            doc["body"],
            " ".join(doc["guidance"]),
            " ".join(t for t in doc["tags"] if isinstance(t, str)),
        ] if p
    )


# ---------------------------------------------------------------------------
def collect_documents() -> List[Dict]:
    docs: List[Dict] = []

    if MAIN_KB.exists():
        entries = json.loads(MAIN_KB.read_text(encoding="utf-8"))
        for e in entries:
            docs.append(normalize_technique(e, f"main_kb/{e.get('id', 'unknown')}"))
        print(f"  main KB: {len(entries)} technique entries")
    else:
        print(f"  WARNING: {MAIN_KB} not found, skipping")

    for directory, normalizer, label in [
        (HIGH_DISTRESS_DIR, normalize_high_distress, "high_distress"),
        (INSIGHT_DIR, normalize_insight, "insight_generation"),
    ]:
        if not directory.exists():
            print(f"  WARNING: {directory} not found, skipping")
            continue
        files = sorted(directory.glob("*.json"))
        for fp in files:
            try:
                entry = json.loads(fp.read_text(encoding="utf-8"))
                docs.append(normalizer(entry, f"{label}/{fp.stem}"))
            except Exception as e:
                print(f"  ERROR parsing {fp.name}: {e}")
        print(f"  {label}: {len(files)} documents")

    return docs


def main():
    print("Collecting knowledge documents...")
    docs = collect_documents()
    if not docs:
        print("No documents found. Nothing to ingest.")
        sys.exit(1)
    print(f"Total: {len(docs)} documents\n")

    ks = KnowledgeService()
    ks.ensure_collection()

    points = []
    for doc in docs:
        vector = ks.embed(doc_to_embed_text(doc))
        point_id = str(uuid.uuid5(uuid.NAMESPACE_URL, doc["id"]))
        points.append(qmodels.PointStruct(id=point_id, vector=vector, payload=doc))
        print(f"  embedded [{doc['doc_type']}] {doc['title']}")

    ks.qdrant.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"\nUpserted {len(points)} points into '{COLLECTION_NAME}'. Done.")


if __name__ == "__main__":
    main()
