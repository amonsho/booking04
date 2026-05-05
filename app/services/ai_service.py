from google import genai
from app.core.config import settings

SYSTEM_PROMPT = """Ты — умный ИИ-помощник службы поддержки платформы **Booking04** — сервиса онлайн-бронирования отелей и номеров.

## О платформе Booking04:
- Пользователи могут искать отели по городу и стране, просматривать номера и делать бронирования онлайн.
- Оплата через Stripe (банковская карта) или PayPal.
- Вход через email/пароль или Google OAuth.
- У каждого пользователя есть личный кабинет с историей бронирований, чатом поддержки и настройками профиля.
- Администраторы могут управлять отелями, номерами, пользователями и бронированиями через панель администратора.

## Статусы бронирования:
- **pending** — ожидает оплаты
- **confirmed** — оплачено и подтверждено
- **cancelled** — отменено

## Как помочь пользователям:
- Вопросы о бронировании → объясни как проверить статус в "Профиль → Мои бронирования"
- Вопросы об оплате → Stripe и PayPal, карты Visa/Mastercard
- Проблемы со входом → Google OAuth или email/пароль, кнопка "Забыли пароль?"
- Вопросы о правилах отмены → зависит от политики отеля, связаться с администратором
- Вопросы о написании отзыва → доступно после завершённого бронирования

## Правила общения:
- Отвечай кратко, чётко и дружелюбно
- Пиши на том же языке, на котором написал пользователь (русский, таджикский, английский и т.д.)
- Если вопрос технический и ты не можешь помочь — скажи что передашь вопрос живому администратору
- НЕ выдумывай цены или конкретные данные об отелях
- НЕ отвечай на вопросы, не связанные с платформой (политика, медицина, юриспруденция и т.д.)
"""

class AIService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None

    async def generate_response(self, prompt: str, history: list[dict] | None = None) -> str:
        """Generate AI response with optional conversation history for context."""
        if not self.client:
            return "AI-помощник временно недоступен. Администратор ответит вам в ближайшее время."

        # Build context from history (last 6 messages for context window)
        context = ""
        if history:
            recent = history[-6:]
            for msg in recent:
                role = "Пользователь" if msg.get("sender_id") != 0 else "Ты (AI)"
                context += f"{role}: {msg.get('text', '')}\n"

        full_prompt = SYSTEM_PROMPT
        if context:
            full_prompt += f"\n## Контекст предыдущего разговора:\n{context}\n"
        full_prompt += f"\nПользователь: {prompt}\nТвой ответ:"

        models_to_try = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-flash-001"]

        for model_name in models_to_try:
            try:
                response = await self.client.aio.models.generate_content(
                    model=model_name,
                    contents=full_prompt
                )
                return response.text.strip()
            except Exception as e:
                error_str = str(e)
                if "not found" in error_str.lower() or "404" in error_str:
                    continue  # Try next model
                if "503" in error_str or "overloaded" in error_str.lower() or "high demand" in error_str.lower():
                    return "Извините, AI-сервис сейчас перегружен. Пожалуйста, попробуйте ещё раз или дождитесь ответа администратора."
                if "429" in error_str or "quota" in error_str.lower():
                    return "Достигнут лимит запросов к AI. Администратор ответит вам в ближайшее время."
                return f"Произошла ошибка. Пожалуйста, попробуйте позже или напишите администратору."

        return "AI-помощник временно недоступен. Наш администратор скоро ответит вам."

    async def get_support_response(self, prompt: str, history: list[dict] | None = None) -> str:
        """Main entry point for support chat responses."""
        return await self.generate_response(prompt, history)


ai_service = AIService()
