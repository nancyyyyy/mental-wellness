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
    memories = memory_service.retrieve_relevant_memories(
        state["user_id"], 
        limit=6
    )
    state["retrieved_memories"] = memories
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
        memory_context = "\n\nRelevant past context:\n"
        for mem in state["retrieved_memories"][-4:]:
            memory_context += f"- {mem.get('text', '')}\n"

    knowledge_context = ""
    if state.get("retrieved_knowledge"):
        knowledge_context = "\n\nAvailable calming techniques and insights:\n"
        for item in state["retrieved_knowledge"]:
            title = item.get("title", "")
            explanation = item.get("detailed_explanation", "")
            steps = item.get("step_by_step_exercise", [])
            knowledge_context += f"\n**{title}**\n{explanation}\n"
            if steps:
                knowledge_context += "How to practice: " + " | ".join(steps[:3]) + "\n"

    prompt = f"""You are a warm, wise, and emotionally intelligent companion.

You respond like an experienced therapist who is fully present. You do not follow rigid scripts. You adapt to the user's emotional state.

{memory_context}
{knowledge_context}

User said: "{state['user_input']}"

Emotional Intensity Guidelines:

- Level 0 (Casual): Keep responses light, warm, and short. No therapeutic intervention needed.
- Level 1 (Mild distress): Show understanding and gentle curiosity. 1-2 questions maximum if natural.
- Level 2 (Significant distress): First acknowledge. Then explain briefly what may be happening. Offer one simple calming technique early. Then explore gently. Maximum 1 meaningful question.
- Level 3 (High distress): Slow down. Prioritize emotional regulation and reassurance first. Offer immediate calming support. Provide presence and containment before any exploration. Questions are optional.
- Level 4 (Crisis): Focus on safety, compassion, and connection. Encourage human support. Stay present. Avoid analysis or multiple techniques.

General Rules:

- When the user is in significant or high distress, help them feel calmer and supported before trying to understand or analyze.
- Use memory only when it adds natural value (clear recurring pattern or connection). Never force it.
- Use techniques from the knowledge base only when genuinely helpful. Prioritize simple calming practices when distress is present.
- Questions should feel organic. Do not ask questions just to continue the conversation.
- Match the user's emotional tone. Be calm, warm, and non-judgmental.
- The user should feel heard and supported, not interviewed.

Response:"""
    
    response = llm.invoke(prompt)
    state["response"] = response.content
    
    # Store new memory
    memory_service.extract_and_store_memories(
        state["user_id"], 
        state["user_input"], 
        state["response"]
    )
    
    return state

# Build the graph
workflow = StateGraph(AgentState)
workflow.add_node("detect_emotion", emotion_analysis)
workflow.add_node("risk", risk_detection)
workflow.add_node("memory_retrieve", memory_retrieval)
workflow.add_node("knowledge", knowledge_retrieval)
workflow.add_node("generate_response", response_generation)

workflow.set_entry_point("detect_emotion")
workflow.add_edge("detect_emotion", "risk")
workflow.add_edge("risk", "memory_retrieve")
workflow.add_edge("memory_retrieve", "knowledge")
workflow.add_edge("knowledge", "generate_response")
workflow.add_edge("generate_response", END)

graph = workflow.compile()
