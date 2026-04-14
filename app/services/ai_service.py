from google import genai
from app.core.config import settings

class AIService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if self.api_key:
            # Using the modern google-genai SDK
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None

    async def generate_response(self, prompt: str, system_prompt: str = "Вы — универсальный полезный помощник. Вы можете отвечать на любые вопросы пользователя, давать советы и помогать с различными задачами, включая бронирование отелей в сервисе 'Booking04'."):
        if not self.client:
            return "AI Service is not configured. Please add GEMINI_API_KEY to your environment."
        
        try:
            # Using 'gemini-flash-latest' which is confirmed in the model list
            response = await self.client.aio.models.generate_content(
                model='gemini-flash-latest',
                contents=f"{system_prompt}\n\nUser Question: {prompt}"
            )
            return response.text
        except Exception as e:
            # If 1.5-flash fails, try falling back to a versioned model or pro
            try:
                response = await self.client.aio.models.generate_content(
                    model='gemini-1.5-flash-001',
                    contents=f"{system_prompt}\n\nUser Question: {prompt}"
                )
                return response.text
            except Exception as e2:
                return f"Error communicating with Gemini AI: {str(e)}"

ai_service = AIService()
