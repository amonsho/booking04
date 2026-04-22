from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.websocket.chat_service import ChatService
from app.services.ai_service import AIService
import json
import asyncio

chat_router = APIRouter(prefix="/chat", tags=["Chat"])
ai_service = AIService()

# Dictionary to store active WebSocket connections: {chat_id: {user_id: websocket}}
connections = {}

@chat_router.websocket("/ws/{user_id}/{chat_id}")
async def chat_ws(websocket: WebSocket, user_id: int, chat_id: int):
    await websocket.accept()
    
    # Identify user role
    from app.db.database import async_session
    from app.models.user import User
    from app.models.enums import UserRole
    from sqlalchemy import select
    
    is_admin = False
    async with async_session() as db:
        user_result = await db.execute(select(User).where(User.id == user_id))
        db_user = user_result.scalars().first()
        if db_user and db_user.role == UserRole.ADMIN:
            is_admin = True

    if chat_id not in connections:
        connections[chat_id] = {}

    connections[chat_id][user_id] = {"socket": websocket, "is_admin": is_admin}

    try:
        # Send history on connect
        history = await ChatService.get_messages(chat_id)
        # Convert SQLAlchemy objects to dict for JSON serialization
        history_list = []
        for msg in history:
            history_list.append({
                "id": msg.id,
                "sender_id": msg.sender_id,
                "chat_id": msg.chat_id,
                "text": msg.text,
                "create_at": str(msg.create_at) if hasattr(msg, 'create_at') else None
            })
        await websocket.send_text(json.dumps(history_list))

        while True:
            raw_text = await websocket.receive_text()
            
            # Try to parse as JSON (Admin sends JSON, User widget sends text)
            try:
                data = json.loads(raw_text)
                text = data.get("text", raw_text) if isinstance(data, dict) else raw_text
            except:
                text = raw_text
            
            # Save message
            await ChatService.save_message(sender_id=user_id, chat_id=chat_id, text=text)

            # Broadcast to everyone in this chat (including sender for confirmation)
            if chat_id in connections:
                msg_json = json.dumps({
                    "sender_id": user_id,
                    "text": text,
                    "chat_id": chat_id,
                    "id": int(asyncio.get_event_loop().time() * 1000) # Temp ID
                })
                for uid, conn_info in connections[chat_id].items():
                    try:
                        await conn_info["socket"].send_text(msg_json)
                    except:
                        pass

            # AI Logic: respond if message is from user (not admin 0) and no admin is present
            # We assume user_id = chat_id means it's the owner of the chat
            is_owner = (user_id == chat_id)
            has_admin = any(info.get("is_admin") for uid, info in connections.get(chat_id, {}).items())

            if is_owner:
                # Trigger AI in background to not block the socket
                role = "user" # Owner is always the user
                asyncio.create_task(handle_ai_response(chat_id, text, not has_admin, role))
            elif user_id != 0:
                # If someone else (admin) writes, we might want AI to know it's an admin
                # but usually AI doesn't respond to admin messages to avoid loops.
                # However, for the 'role' context:
                role = "admin"

    except WebSocketDisconnect:
        if chat_id in connections and user_id in connections[chat_id]:
            del connections[chat_id][user_id]
            if not connections[chat_id]:
                del connections[chat_id]

async def handle_ai_response(chat_id: int, user_text: str, show_offline_notice: bool = False, user_role: str = "user"):
    # Small delay for natural feel
    await asyncio.sleep(1)
    
    ai_response = await ai_service.get_support_response(user_text, user_role)
    
    # Add info that admin is away ONLY if requested
    if show_offline_notice:
        ai_response = f"{ai_response}\n\n(Примечание: Администратора сейчас нет в сети, он ответит вам, как только зайдет в чат)"
    
    # Save to DB
    await ChatService.save_message(sender_id=0, chat_id=chat_id, text=ai_response)
    
    # Broadcast to the user
    if chat_id in connections:
        msg_json = json.dumps({
            "sender_id": 0,
            "text": ai_response,
            "chat_id": chat_id,
            "id": int(asyncio.get_event_loop().time() * 1000)
        })
        for uid, info in connections[chat_id].items():
            try:
                await info["socket"].send_text(msg_json)
            except:
                pass

@chat_router.get("/messages/{chat_id}")
async def get_messages_endpoint(chat_id: int):
    history = await ChatService.get_messages(chat_id)
    history_list = []
    for msg in history:
        history_list.append({
            "id": msg.id,
            "sender_id": msg.sender_id,
            "chat_id": msg.chat_id,
            "text": msg.text,
            "create_at": str(msg.create_at) if hasattr(msg, 'create_at') else None
        })
    return history_list

@chat_router.get("/admin/rooms")
async def get_admin_rooms():
    # Return unique chat_ids that have messages
    from app.db.database import async_session
    from app.models.messages import Messages
    from sqlalchemy import select, func
    
    async with async_session() as db:
        # Get last message for each chat
        subq = select(
            Messages.chat_id,
            func.max(Messages.id).label('max_id')
        ).group_by(Messages.chat_id).subquery()
        
        query = select(Messages).join(
            subq, Messages.id == subq.c.max_id
        ).order_by(Messages.id.desc())
        
        result = await db.execute(query)
        last_messages = result.scalars().all()
        
        rooms = []
        for msg in last_messages:
            rooms.append({
                "chat_id": msg.chat_id,
                "user_name": f"User {msg.chat_id}",
                "last_message": msg.text,
                "last_time": "Недавно",
                "unread_count": 0
            })
        return rooms