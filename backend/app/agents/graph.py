import json
from typing import TypedDict, Dict, Any, List

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from ..core.config import settings
from ..services.memory_service import MemoryService
from ..services.knowledge_service import KnowledgeService


class AgentState(TypedDict):
    user_input: str
    user_id: str
    conversation_id: int
    chat_history: List[Dict]
    emotion: Dict[str, Any]
    risk_level: str          # "safe" | "elevated" | "crisis"
    category: str
    retrieved_knowledge: List[Dict]
    retrieved_memories: List[Dict]
    response: str


def build_llm(temperature: float = 0.7) -> ChatOpenAI:
    if settings.LLM_PROVIDER == "openai":
        return ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_MODEL,
            temperature=temperature,
        )
    # Ollama fallback (OpenAI-compatible endpoint)
    return ChatOpenAI(
        base_url=f"{settings.OLLAMA_BASE_URL}/v1",
        api_key="ollama",
        model=settings.OLLAMA_MODEL,
        temperature=temperature,
    )


llm = build_llm(temperature=0.7)
classifier_llm = build_llm(temperature=0.0)  # deterministic for analysis

memory_service = MemoryService()
knowledge_service = KnowledgeService()


# ---------------------------------------------------------------------------
# Node 1: Emotion analysis (real LLM classification, was a stub)
# ---------------------------------------------------------------------------
EMOTION_PROMPT = """Analyze the emotional content of this message from a mental wellness app user.

Message: "{user_input}"

Respond with ONLY a JSON object, no markdown fences, no other text:
{{
  "emotion": "<primary emotion, e.g. sadness, anxiety, anger, joy, loneliness, overwhelm, neutral>",
  "intensity": <0-4 where 0=casual chat, 1=mild distress, 2=significant distress, 3=high distress, 4=crisis-level despair>,
  "confidence": <0.0-1.0>,
  "category": "<best matching topic: emotional_wellness | anxiety | depression | stress | relationships | self_esteem | grief | sleep | general>"
}}"""


def emotion_analysis(state: AgentState) -> AgentState:
    try:
        raw = classifier_llm.invoke(
            EMOTION_PROMPT.format(user_input=state["user_input"])
        ).content
        raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        parsed = json.loads(raw)
        state["emotion"] = {
            "emotion": parsed.get("emotion", "neutral"),
            "intensity": int(parsed.get("intensity", 0)),
            "confidence": float(parsed.get("confidence", 0.5)),
        }
        state["category"] = parsed.get("category", "general")
    except Exception as e:
        print(f"Emotion analysis error: {e}")
        state["emotion"] = {"emotion": "neutral", "intensity": 1, "confidence": 0.3}
        state["category"] = "general"
    return state


# ---------------------------------------------------------------------------
# Node 2: Risk detection (real, was a stub) — conservative by design
# ---------------------------------------------------------------------------
RISK_PROMPT = """You are a safety classifier for a mental wellness support app.

Classify the risk level of this user message:
"{user_input}"

Levels:
- "safe": everyday emotions, stress, sadness, venting — no indication of danger
- "elevated": intense hopelessness, feeling like a burden, passive statements about not wanting to exist, but no stated intent or plan
- "crisis": any indication of intent to harm self or others, an active plan, saying goodbye, or immediate danger

When uncertain between two levels, choose the HIGHER one.

Respond with ONLY one word: safe, elevated, or crisis"""


def risk_detection(state: AgentState) -> AgentState:
    try:
        raw = classifier_llm.invoke(
            RISK_PROMPT.format(user_input=state["user_input"])
        ).content.strip().lower()
        state["risk_level"] = raw if raw in ("safe", "elevated", "crisis") else "elevated"
    except Exception as e:
        print(f"Risk detection error: {e}")
        state["risk_level"] = "elevated"  # fail toward caution
    return state


def route_after_risk(state: AgentState) -> str:
    return "crisis_response" if state["risk_level"] == "crisis" else "memory_retrieve"


# ---------------------------------------------------------------------------
# Crisis path: skip RAG/analysis, prioritize safety and human connection
# ---------------------------------------------------------------------------
CRISIS_PROMPT = """You are a warm, calm, compassionate companion. The user may be in crisis.

User said: "{user_input}"

Your only goals, in order:
1. Acknowledge their pain with genuine warmth. Do not analyze or ask probing questions.
2. Tell them clearly that they deserve support from a real person right now, and gently encourage them to reach out to a crisis helpline, a trusted person, or local emergency services.
3. Remind them they are not alone and you will stay present with them.

Keep it short (4-6 sentences), warm, and human. No techniques, no lists, no exercises."""


def crisis_response(state: AgentState) -> AgentState:
    try:
        response = llm.invoke(CRISIS_PROMPT.format(user_input=state["user_input"]))
        state["response"] = response.content
    except Exception:
        state["response"] = (
            "I'm really glad you told me this, and I'm so sorry you're in this much pain. "
            "What you're feeling matters, and you deserve support from a real person right now. "
            "Please consider reaching out to a crisis helpline or someone you trust — you don't "
            "have to go through this alone. I'm here with you."
        )
    return state


# ---------------------------------------------------------------------------
# Standard path
# ---------------------------------------------------------------------------
def memory_retrieval(state: AgentState) -> AgentState:
    state["retrieved_memories"] = memory_service.retrieve_relevant_memories(
        state["user_id"], limit=6
    )
    return state


def knowledge_retrieval(state: AgentState) -> AgentState:
    try:
        intensity = state["emotion"].get("intensity", 0)
        # Casual chat needs no RAG
        if intensity == 0:
            state["retrieved_knowledge"] = []
            return state

        results: List[Dict] = []
        # At high distress, pull response protocols first
        if intensity >= 3:
            results += knowledge_service.retrieve(
                query=state["user_input"],
                doc_type="high_distress",
                limit=2,
            )
        # Always add relevant techniques
        results += knowledge_service.retrieve(
            query=state["user_input"],
            doc_type="technique",
            limit=3,
        )
        state["retrieved_knowledge"] = results
    except Exception as e:
        print(f"Knowledge retrieval error: {e}")
        state["retrieved_knowledge"] = []
    return state


def response_generation(state: AgentState) -> AgentState:
    memory_context = ""
    if state.get("retrieved_memories"):
        memory_context = "\n\nRelevant past context:\n"
        for mem in state["retrieved_memories"][-4:]:
            memory_context += f"- {mem.get('text', '')}\n"

    knowledge_context = ""
    if state.get("retrieved_knowledge"):
        knowledge_context = "\n\nRetrieved knowledge base material (ground your response in this):\n"
        for item in state["retrieved_knowledge"]:
            knowledge_context += f"\n**{item.get('title', '')}** [{item.get('doc_type', '')}]\n"
            if item.get("body"):
                knowledge_context += item["body"] + "\n"
            if item.get("guidance"):
                knowledge_context += "Guidance: " + " | ".join(item["guidance"][:4]) + "\n"
            if item.get("example_response"):
                knowledge_context += f"Example tone/response: {item['example_response']}\n"

    emotion = state.get("emotion", {})
    detected = (
        f"\nDetected emotional state: {emotion.get('emotion', 'neutral')} "
        f"(intensity level {emotion.get('intensity', 0)} of 4).\n"
        "Respond according to this intensity level using the guidelines below.\n"
    )

    system_prompt = f"""You are a warm, wise, and emotionally intelligent companion.

You respond like an experienced, supportive listener who is fully present with the user. You adapt your approach based on the user's emotional state. You are NOT a therapist or doctor and never diagnose.
{detected}{memory_context}{knowledge_context}

Continue the conversation naturally, staying consistent with what's already been said.

### Emotional Intensity Guidelines

**Level 0 (Casual)**: Keep responses light, warm, and short. No therapeutic intervention needed.

**Level 1 (Mild Distress)**: Show understanding and gentle curiosity. You may explore gently. Maximum 1-2 natural questions.

**Level 2 (Significant Distress)**:
- First acknowledge and validate.
- Briefly explain what may be happening.
- Offer one relevant calming technique from the knowledge base if available.
- Then explore gently if appropriate.
- Maximum 1 meaningful question.

**Level 3 (High Distress)**:
**Primary Goal: Emotional Stabilization**
Follow this order strictly:
1. Acknowledge and emotionally contain the experience.
2. Reassure the user they are not alone.
3. Briefly explain what may be happening in the mind/body using the knowledge base.
4. Offer **one immediate grounding or calming technique** from the available knowledge base.
5. Stay present and supportive.
6. **Avoid interrogating** the user.
7. **Avoid multiple questions**.
8. Do not rush into insight or exploration.

### General Rules
- Prioritize **Support → Regulation → Insight** when distress is high. Do not start with exploration.
- Use techniques and insights from the retrieved knowledge base when available. Do not rely only on general knowledge.
- Use memory only when it adds natural value. Never force it.
- Match the user's emotional tone. Be calm, warm, and non-judgmental.
- The user should feel supported and contained, not interviewed.
- If the topic is beyond emotional support (medical, legal, diagnosis), gently suggest a qualified professional."""

    messages: List[Any] = [SystemMessage(content=system_prompt)]
    for turn in state.get("chat_history", []):
        if turn.get("role") == "assistant":
            messages.append(AIMessage(content=turn.get("content", "")))
        else:
            messages.append(HumanMessage(content=turn.get("content", "")))
    messages.append(HumanMessage(content=state["user_input"]))

    response = llm.invoke(messages)
    state["response"] = response.content

    memory_service.extract_and_store_memories(
        state["user_id"], state["user_input"], state["response"]
    )
    return state


# ---------------------------------------------------------------------------
# Graph
# ---------------------------------------------------------------------------
workflow = StateGraph(AgentState)
workflow.add_node("detect_emotion", emotion_analysis)
workflow.add_node("risk", risk_detection)
workflow.add_node("crisis_response", crisis_response)
workflow.add_node("memory_retrieve", memory_retrieval)
workflow.add_node("knowledge", knowledge_retrieval)
workflow.add_node("generate_response", response_generation)

workflow.set_entry_point("detect_emotion")
workflow.add_edge("detect_emotion", "risk")
workflow.add_conditional_edges(
    "risk",
    route_after_risk,
    {"crisis_response": "crisis_response", "memory_retrieve": "memory_retrieve"},
)
workflow.add_edge("crisis_response", END)
workflow.add_edge("memory_retrieve", "knowledge")
workflow.add_edge("knowledge", "generate_response")
workflow.add_edge("generate_response", END)

graph = workflow.compile()
