from typing import TypedDict, Dict, Any, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from ..core.config import settings
from ..services.memory_service import MemoryService

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

def emotion_analysis(state: AgentState) -> AgentState:
    state["emotion"] = {"emotion": "neutral", "intensity": 5, "confidence": 0.8}
    return state

def risk_detection(state: AgentState) -> AgentState:
    state["risk_level"] = "safe"
    return state

def memory_retrieval(state: AgentState) -> AgentState:
    """Retrieve relevant memories before generating response"""
    memories = memory_service.retrieve_relevant_memories(
        state["user_id"], 
        state["user_input"],
        limit=5
    )
    state["retrieved_memories"] = memories
    return state

def knowledge_retrieval(state: AgentState) -> AgentState:
    state["retrieved_knowledge"] = []
    return state

def response_generation(state: AgentState) -> AgentState:
    # Build memory context
    memory_context = ""
    if state.get("retrieved_memories"):
        memory_context = "\n\nRelevant things I remember about you:\n"
        for mem in state["retrieved_memories"][-3:]:  # Use last 3 memories
            memory_context += f"- {mem.get('text', '')}\n"
    
    prompt = f"""You are a compassionate, emotionally intelligent companion who genuinely remembers and cares about the user.

{memory_context}

Current user message: {state['user_input']}

Guidelines:
- Respond warmly and naturally, like someone who knows them.
- If relevant memories exist, gently reference them when it adds value.
- Validate their emotions.
- Ask thoughtful follow-up questions when appropriate.
- Never dump all memories at once.
- Be supportive without being overly clinical.

Response:"""
    
    response = llm.invoke(prompt)
    state["response"] = response.content
    
    # Store new memory after generating response
    memory_service.extract_and_store_memories(
        state["user_id"], 
        state["user_input"], 
        state["response"]
    )
    
    return state

# Build the graph with memory
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