from app.models.messages import Messages
from app.db.database import async_session
from sqlalchemy import select

class ChatService:
    
    @staticmethod
    async def save_message(sender_id: int, chat_id: int, text: str):
        async with async_session() as db: 
            msg = Messages(
                sender_id=sender_id,
                chat_id=chat_id,
                text=text
            )
            db.add(msg)
            await db.commit()
        
    @staticmethod
    async def get_messages(chat_id: int):
        async with async_session() as db:
            result = await db.execute(
                select(Messages).where(Messages.chat_id == chat_id)
            )
            messages = result.scalars().all()
            return messages