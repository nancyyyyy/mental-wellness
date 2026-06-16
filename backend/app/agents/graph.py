from typing import TypedDict, Dict, Any, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from ..core.config import settings
from ..services.memory_service import MemoryService
from ..services.knowledge_service import KnowledgeService

class AgentState(TypedDict):
    user_input: str
    user_id: str
    emotion: Dict[str, Any]
    risk_level: str
    category: str
    retrieved_knowledge: List[Dict]
    retrieved_memories: List[Dict]
    response: str

# Initialize LLM
if settings.LLM_PROVIDER == "groq":
    llm = ChatGroq(
        groq_api_key=settings.GROQ_API_KEY,
        model_name=settings.GROQ_MODEL,
        temperature=0.7,
    )
elif settings.LLM_PROVIDER == "openai":
    llm = ChatOpenAI(
        openai_api_key=settings.OPENAI_API_KEY,
        model=settings.OPENAI_MODEL,
        temperature=0.7,
    )
else:
    llm = ChatOpenAI(
        base_url=f"{settings.OLLAMA_BASE_URL}/v1",
        api_key="ollama",
        model=settings.OLLAMA_MODEL,
        temperature=0.7,
    )

memory_service = MemoryService()
knowledge_service = KnowledgeService()

def emotion_analysis(state: AgentState) -> AgentState:
    state["emotion"] = {"emotion": "neutral", "intensity": 5, "confidence": 0.8}
    return state

def risk_detection(state: AgentState) -> AgentState:
    state["risk_level"] = "safe"
    return state

def memory_retrieval(state: AgentState) -> AgentState:
    state["retrieved_memories"] = []
    return state

def knowledge_retrieval(state: AgentState) -> AgentState:
    try:
        knowledge = knowledge_service.retrieve(
            query=state["user_input"],
            category="emotional_wellness",
            limit=5
        )
        state["retrieved_knowledge"] = knowledge
    except Exception as e:
        print(f"Knowledge retrieval error: {e}")
        state["retrieved_knowledge"] = []
    return state

def response_generation(state: AgentState) -> AgentState:
    memory_context = ""
    if state.get("retrieved_memories"):
        memory_context = "\n\nThings I remember about you:\n"
        for mem in state["retrieved_memories"][-4:]:
            memory_context += f"- {mem.get('text', '')}\n"

    knowledge_context = ""
    if state.get("retrieved_knowledge"):
        knowledge_context = "\n\nHelpful techniques from wellness resources:\n"
        for item in state["retrieved_knowledge"]:
            title = item.get("title", "")
            explanation = item.get("detailed_explanation", "")
            steps = item.get("step_by_step_exercise", [])
            knowledge_context += f"\n**{title}**\n{explanation}\n"
            if steps:
                knowledge_context += "How to practice: " + " | ".join(steps[:3]) + "\n"

    prompt = f"""You are a warm, calm, and emotionally present companion.

{memory_context}
{knowledge_context}

User said: {state['user_input']}

Guidelines for your response:
- Keep it natural and conversational (do NOT label sections like "Step 1" or "Step 2").
- Start with a short, genuine acknowledgment of what the user shared.
- If relevant, gently explain what might be happening emotionally or psychologically (use the techniques above when helpful).
- If it fits naturally, suggest 1 practical technique or small step from the resources above. Explain briefly why it might help and how to try it.
- End with one thoughtful, open-ended question that helps deepen understanding (about triggers, patterns, needs, or feelings).
- Keep the overall response relatively short and easy to read.
- Never sound robotic or like you're following a checklist.

Response:"""
    
    response = llm.invoke(prompt)
    state["response"] = response.content
    return state

# Build the graph
workflow = StateGraph(AgentState)
workflow.add_node("emotion", emotion_analysis)
workflow.add_node("risk", risk_detection)
workflow.add_node("memory_retrieve", memory_retrieval)
workflow.add_node("knowledge", knowledge_retrieval)
workflow.add_node("response", response_generation)

workflow.set_entry_point("emotion")
workflow.add_edge("emotion", "risk")
workflow.add_edge("risk", "memory_retrieve")
workflow.add_edge("memory_retrieve", "knowledge")
workflow.add_edge("knowledge", "response")
workflow.add_edge("response", END)

graph = workflow.compile()
