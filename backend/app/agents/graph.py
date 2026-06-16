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
        if not knowledge:
            knowledge = knowledge_service.retrieve(
                query=state["user_input"],
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
        memory_context = "\n\nRelevant things I remember about you:\n"
        for mem in state["retrieved_memories"][-4:]:
            memory_context += f"- {mem.get('text', '')}\n"

    knowledge_context = ""
    if state.get("retrieved_knowledge"):
        knowledge_context = "\n\nRelevant practices and techniques from evidence-based resources:\n"
        for item in state["retrieved_knowledge"]:
            title = item.get("title", "")
            explanation = item.get("detailed_explanation", "")
            steps = item.get("step_by_step_exercise", [])
            
            knowledge_context += f"\n**{title}**\n"
            knowledge_context += f"{explanation}\n"
            if steps:
                knowledge_context += "Steps: " + " | ".join(steps[:3]) + "\n"

    prompt = f"""You are a warm, calm, and emotionally intelligent companion.

{memory_context}
{knowledge_context}

User said: {state['user_input']}

RESPONSE FRAMEWORK:

1. Brief Acknowledgement (1 sentence)
   - Acknowledge what they shared naturally.

2. Insight (Optional but helpful)
   - Gently explain what may be happening, using knowledge when relevant.

3. Practices & Healing Guidance (When user shows distress, recurring patterns, or asks for help)
   - Recommend **at most 1 practice** from the knowledge above.
   - Use this exact format:

     **Practice:** [Name of the practice]
     **Why It May Help:** [Brief explanation tied to their situation]
     **Steps:**
     1. ...
     2. ...
     **Duration:** [e.g., 3-5 minutes]
     **Expected Benefit:** [What they might experience]
     **Reflection:** [One gentle question]

   - Only recommend practices that exist in the "Relevant practices and techniques" section.
   - Prioritize quality and relevance over quantity.
   - Keep instructions simple and beginner-friendly.

4. Follow-up Question
   - Ask one thoughtful question (about triggers, patterns, needs, or how they feel about trying a practice).

Rules:
- Keep the overall response concise and readable.
- Sound supportive and non-clinical.
- Never overwhelm the user with too many suggestions.

Response:"""
    
    response = llm.invoke(prompt)
    state["response"] = response.content
    
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