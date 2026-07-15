from typing import List, Dict, Optional
from ..db.base import get_db
from ..db.models import Conversation, Message


class ConversationService:
    def get_or_create(self, user_id: str, conversation_id: Optional[int] = None) -> Conversation:
        """Return the conversation for conversation_id if it belongs to user_id,
        otherwise start a new one for that user."""
        db = next(get_db())
        try:
            if conversation_id is not None:
                conversation = (
                    db.query(Conversation)
                    .filter(Conversation.id == conversation_id, Conversation.user_id == user_id)
                    .first()
                )
                if conversation:
                    return conversation

            conversation = Conversation(user_id=user_id)
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            return conversation
        finally:
            db.close()

    def add_message(self, conversation_id: int, role: str, content: str):
        db = next(get_db())
        try:
            message = Message(conversation_id=conversation_id, role=role, content=content)
            db.add(message)
            db.commit()
        finally:
            db.close()

    def get_recent_turns(self, conversation_id: int, limit: int = 10) -> List[Dict]:
        """Most recent `limit` messages for a conversation, oldest first."""
        db = next(get_db())
        try:
            messages = (
                db.query(Message)
                .filter(Message.conversation_id == conversation_id)
                .order_by(Message.created_at.desc())
                .limit(limit)
                .all()
            )
            return [{"role": m.role, "content": m.content} for m in reversed(messages)]
        finally:
            db.close()
