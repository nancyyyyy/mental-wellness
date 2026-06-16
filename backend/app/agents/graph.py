from typing import TypedDict, Dict, Any, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI

class AgentState(TypedDict):
    user_input: str
    user_id: str
    emotion: Dict[str, Any]
    risk_level: str
    category: str
    retrieved_knowledge: List[Dict]
    response: str

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

def emotion_analysis(state):
    state["emotion"] = {"emotion": "neutral", "intensity": 5, "confidence": 0.8}
    return state

def risk_detection(state):
    state["risk_level"] = "safe"
    return state

def knowledge_retrieval(state):
    state["retrieved_knowledge"] = []
    return state

def response_generation(state):
    prompt = f"Respond compassionately to: {state['user_input']}. Use grounding from knowledge if available."
    response = llm.invoke(prompt)
    state["response"] = response.content
    return state

workflow = StateGraph(AgentState)
workflow.add_node("emotion", emotion_analysis)
workflow.add_node("risk", risk_detection)
workflow.add_node("knowledge", knowledge_retrieval)
workflow.add_node("response", response_generation)
workflow.set_entry_point("emotion")
workflow.add_edge("emotion", "risk")
workflow.add_edge("risk", "knowledge")
workflow.add_edge("knowledge", "response")
workflow.add_edge("response", END)
graph = workflow.compile()