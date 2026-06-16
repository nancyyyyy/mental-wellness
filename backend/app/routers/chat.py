from fastapi import APIRouter
from ..agents.graph import graph

router = APIRouter()

@router.post("/message")
async def send_message(payload: dict):
    result = graph.invoke({
        "user_input": payload.get("content", ""),
        "user_id": payload.get("user_id", "demo")
    })
    return {"response": result.get("response", "I'm here to support you.")}