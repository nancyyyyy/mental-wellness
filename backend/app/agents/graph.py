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
        state["user_input"],
        limit=5
    )
    state["retrieved_memories"] = memories
    return state

def knowledge_retrieval(state: AgentState) -> AgentState:
    """Retrieve relevant knowledge from the structured knowledge base"""
    try:
        # For now, search in emotional_wellness collection
        # Later we can make this dynamic based on topic classification
        knowledge = knowledge_service.retrieve(
            query=state["user_input"],
            category="emotional_wellness",
            limit=4
        )
        state["retrieved_knowledge"] = knowledge
    except Exception as e:
        print(f"Knowledge retrieval error: {e}")
        state["retrieved_knowledge"] = []
    return state

def response_generation(state: AgentState) -> AgentState:
    # Build memory context
    memory_context = ""
    if state.get("retrieved_memories"):
        memory_context = "\n\nThings I remember about you:\n"
        for mem in state["retrieved_memories"][-3:]:
            memory_context += f"- {mem.get('text', '')}\n"

    # Build knowledge context from structured knowledge base
    knowledge_context = ""
    if state.get("retrieved_knowledge"):
        knowledge_context = "\n\nRelevant knowledge from wellness resources:\n"
        for item in state["retrieved_knowledge"]:
            title = item.get("title", "")
            explanation = item.get("detailed_explanation", "")
            exercise = item.get("step_by_step_exercise", [])
            
            knowledge_context += f"\n**{title}**\n"
            knowledge_context += f"{explanation}\n"
            if exercise:
                knowledge_context += "Helpful steps: " + " | ".join(exercise[:2]) + "\n"

    prompt = f"""You are a warm, calm, and emotionally present companion. You remember important things about the user and respond naturally, using evidence-based wellness knowledge when helpful.

{memory_context}
{knowledge_context}

User said: {state['user_input']}

Rules:
- Keep responses relatively short and easy to read (2-4 sentences max).
- Use the provided knowledge naturally when it fits — don't force it.
- Do NOT make assumptions about how the user is feeling unless they clearly said so.
- Be genuine and conversational.
- Validate what they shared.
- Ask one thoughtful follow-up question if appropriate.

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