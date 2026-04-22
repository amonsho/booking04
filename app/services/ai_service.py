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

    async def generate_response(self, prompt: str, user_role: str = "user"):
        system_prompt = f"Вы — универсальный полезный помощник сервиса 'Booking04'. "
        if user_role == "admin":
            system_prompt += "Вы общаетесь с АДМИНИСТРАТОРОМ. Если он спрашивает о сообщениях пользователей, направьте его в 'Админ-панель -> Чат'. "
        else:
            system_prompt += "Вы общаетесь с ПОЛЬЗОВАТЕЛЕМ. Если он спрашивает о своих сообщениях, направьте его в 'Профиль -> Мои сообщения'. "
        
        system_prompt += "Вы можете отвечать на вопросы, давать советы и помогать с бронированием."
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
                error_msg = str(e)
                if "503" in error_msg or "high demand" in error_msg.lower():
                    return "Извините, сервис ИИ сейчас перегружен. Пожалуйста, попробуйте позже или дождитесь ответа администратора."
                return f"Ошибка связи с ИИ: {error_msg}"

    def get_support_response(self, prompt: str, user_role: str = "user"):
        return self.generate_response(prompt, user_role)

ai_service = AIService()
