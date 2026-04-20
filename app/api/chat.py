from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.websocket.chat_service import ChatService

chat_router = APIRouter(prefix="/chat", tags=["Chat"])

# Dictionary to store active WebSocket connections: {chat_id: {user_id: websocket}}
connections = {}

@chat_router.websocket("/ws/{user_id}/{chat_id}")
async def chat_ws(websocket: WebSocket, user_id: int, chat_id: int):
    await websocket.accept()

    if chat_id not in connections:
        connections[chat_id] = {}

    connections[chat_id][user_id] = websocket

    try:
        while True:
            # Wait for messages from the client
            text = await websocket.receive_text()

            # Broadcast the message to all other users in the same chat
            if chat_id in connections:
                for uid, conn in connections[chat_id].items():
                    if uid != user_id:
                        try:
                            await conn.send_text(f"{user_id}: {text}")
                        except Exception:
                            # Handle stale connections
                            pass

            # Save the message to history
            await ChatService.save_message(sender_id=user_id, chat_id=chat_id, text=text)

    except WebSocketDisconnect:
        if chat_id in connections and user_id in connections[chat_id]:
            del connections[chat_id][user_id]
            # Clean up empty chat dictionaries
            if not connections[chat_id]:
                del connections[chat_id]

@chat_router.get("/messages/{chat_id}")
async def get_messages(chat_id: int):
    """
    Retrieve message history for a specific chat.
    """
    return await ChatService.get_messages(chat_id)