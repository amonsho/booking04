from fastapi import APIRouter, HTTPException
from app.services.ai_service import ai_service
from pydantic import BaseModel

router = APIRouter(prefix="/ai", tags=["AI"])

class ChatRequest(BaseModel):
    prompt: str

@router.post("/chat")
async def chat_with_ai(request: ChatRequest):
    response = await ai_service.generate_response(request.prompt)
    if "Error communicating with AI" in response:
        raise HTTPException(status_code=500, detail=response)
    if "AI Service is not configured" in response:
        raise HTTPException(status_code=400, detail=response)
    return {"response": response}
