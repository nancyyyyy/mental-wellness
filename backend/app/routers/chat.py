from fastapi import APIRouter
from ..agents.graph import graph
from ..services.conversation_service import ConversationService

router = APIRouter()
conversation_service = ConversationService()

@router.post("/message")
async def send_message(payload: dict):
    user_id = payload.get("user_id", "demo")
    user_input = payload.get("content", "")
    conversation_id = payload.get("conversation_id")

    conversation = conversation_service.get_or_create(user_id, conversation_id)
    chat_history = conversation_service.get_recent_turns(conversation.id, limit=10)
    conversation_service.add_message(conversation.id, "user", user_input)

    result = graph.invoke({
        "user_input": user_input,
        "user_id": user_id,
        "conversation_id": conversation.id,
        "chat_history": chat_history,
    })
    response = result.get("response", "I'm here to support you.")

    conversation_service.add_message(conversation.id, "assistant", response)

    return {"response": response, "conversation_id": conversation.id}
