from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.websocket.chat_service import ChatService
from app.services.ai_service import AIService
import json
import asyncio

chat_router = APIRouter(prefix="/chat", tags=["Chat"])
ai_service = AIService()

# Active WebSocket connections: {chat_id: {user_id: {"socket": ws, "is_admin": bool}}}
connections: dict[int, dict[int, dict]] = {}


async def _get_user_info(user_id: int) -> dict:
    """Fetch user name and role from DB."""
    from app.db.database import async_session
    from app.models.user import User
    from app.models.enums import UserRole
    from sqlalchemy import select

    async with async_session() as db:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if user:
            return {
                "name": user.name or f"Пользователь #{user_id}",
                "is_admin": user.role == UserRole.ADMIN,
            }
    return {"name": f"Пользователь #{user_id}", "is_admin": False}


@chat_router.websocket("/ws/{user_id}/{chat_id}")
async def chat_ws(websocket: WebSocket, user_id: int, chat_id: int):
    await websocket.accept()

    user_info = await _get_user_info(user_id)
    is_admin = user_info["is_admin"]

    if chat_id not in connections:
        connections[chat_id] = {}

    connections[chat_id][user_id] = {"socket": websocket, "is_admin": is_admin}

    try:
        # Send message history on connect
        history = await ChatService.get_messages(chat_id)
        history_list = [
            {
                "id": msg.id,
                "sender_id": msg.sender_id,
                "chat_id": msg.chat_id,
                "text": msg.text,
                "create_at": str(msg.create_at) if hasattr(msg, "create_at") else None,
            }
            for msg in history
        ]
        await websocket.send_text(json.dumps(history_list))

        while True:
            raw_text = await websocket.receive_text()

            # Parse JSON or plain text
            try:
                data = json.loads(raw_text)
                text = data.get("text", raw_text) if isinstance(data, dict) else raw_text
            except Exception:
                text = raw_text

            text = text.strip()
            if not text:
                continue

            # Save message to DB
            await ChatService.save_message(sender_id=user_id, chat_id=chat_id, text=text)

            # Broadcast to everyone in this chat room
            msg_payload = json.dumps({
                "sender_id": user_id,
                "text": text,
                "chat_id": chat_id,
                "id": int(asyncio.get_event_loop().time() * 1000),
                "create_at": None,
            })

            if chat_id in connections:
                for uid, conn_info in list(connections[chat_id].items()):
                    try:
                        await conn_info["socket"].send_text(msg_payload)
                    except Exception:
                        pass

            # Trigger AI only when the chat owner (user, not admin) writes
            # and no real admin is currently connected in this room
            is_owner = (user_id == chat_id)
            has_live_admin = any(
                info.get("is_admin")
                for uid, info in connections.get(chat_id, {}).items()
                if uid != user_id
            )

            if is_owner and not is_admin:
                # Pass recent history for context
                history_for_ai = [
                    {"sender_id": m.get("sender_id"), "text": m.get("text")}
                    for m in history_list[-10:]
                ]
                asyncio.create_task(
                    handle_ai_response(chat_id, text, history_for_ai, add_admin_notice=not has_live_admin)
                )

    except WebSocketDisconnect:
        if chat_id in connections:
            connections[chat_id].pop(user_id, None)
            if not connections[chat_id]:
                del connections[chat_id]


async def handle_ai_response(
    chat_id: int,
    user_text: str,
    history: list[dict],
    add_admin_notice: bool = False,
):
    """Generate and broadcast AI response."""
    await asyncio.sleep(0.8)  # Small delay for natural feel

    ai_response = await ai_service.get_support_response(user_text, history)

    if add_admin_notice:
        ai_response += "\n\n_(Администратора сейчас нет в сети — он ответит, как только подключится)_"

    await ChatService.save_message(sender_id=0, chat_id=chat_id, text=ai_response)

    if chat_id in connections:
        msg_json = json.dumps({
            "sender_id": 0,
            "text": ai_response,
            "chat_id": chat_id,
            "id": int(asyncio.get_event_loop().time() * 1000),
            "create_at": None,
        })
        for uid, info in list(connections[chat_id].items()):
            try:
                await info["socket"].send_text(msg_json)
            except Exception:
                pass


@chat_router.get("/messages/{chat_id}")
async def get_messages_endpoint(chat_id: int):
    history = await ChatService.get_messages(chat_id)
    return [
        {
            "id": msg.id,
            "sender_id": msg.sender_id,
            "chat_id": msg.chat_id,
            "text": msg.text,
            "create_at": str(msg.create_at) if hasattr(msg, "create_at") else None,
        }
        for msg in history
    ]


@chat_router.get("/admin/rooms")
async def get_admin_rooms():
    """Return list of chat rooms with the last message and real user name."""
    from app.db.database import async_session
    from app.models.messages import Messages
    from app.models.user import User
    from sqlalchemy import select, func

    async with async_session() as db:
        # Get last message per chat_id
        subq = (
            select(Messages.chat_id, func.max(Messages.id).label("max_id"))
            .group_by(Messages.chat_id)
            .subquery()
        )
        query = (
            select(Messages)
            .join(subq, Messages.id == subq.c.max_id)
            .order_by(Messages.id.desc())
        )
        result = await db.execute(query)
        last_messages = result.scalars().all()

        # Fetch real user names for each chat_id (chat_id == user_id by convention)
        chat_ids = [msg.chat_id for msg in last_messages]
        users_result = await db.execute(select(User).where(User.id.in_(chat_ids)))
        users = {u.id: u for u in users_result.scalars().all()}

        rooms = []
        for msg in last_messages:
            user = users.get(msg.chat_id)
            user_name = user.name if user else f"Пользователь #{msg.chat_id}"
            # Strip admin-offline notice from preview
            preview = msg.text
            if "_(Администратора сейчас нет в сети" in preview:
                preview = preview.split("\n\n_(")[0].strip()

            rooms.append({
                "chat_id": msg.chat_id,
                "user_name": user_name,
                "user_email": user.email if user else None,
                "last_message": preview,
                "last_time": "Недавно",
                "unread_count": 0,
            })

        return rooms