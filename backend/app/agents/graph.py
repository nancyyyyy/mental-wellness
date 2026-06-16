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
    # Temporarily disabled to avoid DB type errors with "demo-user"
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
        memory_context = "\n\nRelevant context from previous conversations:\n"
        for mem in state["retrieved_memories"][-5:]:
            memory_context += f"- {mem.get('text', '')}\n"

    knowledge_context = ""
    if state.get("retrieved_knowledge"):
        knowledge_context = "\n\nRelevant therapeutic knowledge:\n"
        for item in state["retrieved_knowledge"]:
            title = item.get("title", "")
            explanation = item.get("detailed_explanation", "")
            steps = item.get("step_by_step_exercise", [])
            knowledge_context += f"\n**{title}**\n{explanation}\n"
            if steps:
                knowledge_context += "Practical steps: " + " | ".join(steps[:4]) + "\n"

    prompt = f"""You are an experienced, emotionally intelligent companion who remembers important details about the user and helps them gain deeper self-understanding over time.

{memory_context}
{knowledge_context}

User's message: {state['user_input']}

Your approach:
- First, understand what the user is actually experiencing and what emotional need might be underneath this message.
- Connect the current situation to previous patterns or conversations when relevant (use memory context naturally, without listing facts).
- Provide meaningful insight when possible — help the user see something they might not have noticed (patterns, triggers, beliefs, or dynamics).
- When appropriate, draw from the therapeutic knowledge above to explain psychological mechanisms or suggest helpful practices.
- Keep your tone calm, curious, non-judgmental, and supportive.
- End with one thoughtful question that helps deepen understanding of their experience, patterns, or needs.

Important:
- Do not over-explain or give long lectures on simple messages.
- Do not force techniques if they don't fit naturally.
- Focus on helping the user feel genuinely understood and gain clarity.

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
