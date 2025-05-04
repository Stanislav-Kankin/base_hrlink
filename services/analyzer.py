from openai import AsyncOpenAI
from utils.logging import logger
from utils.prompts import SYSTEM_PROMPT
from config import config

client = AsyncOpenAI(api_key=config.PROXY_API_KEY)


async def get_answer(question: str) -> str:
    """Получает ответ на вопрос из базы знаний"""
    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question}
            ],
            temperature=0.3,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Ошибка при запросе к OpenAI: {e}")
        return "⚠️ Произошла ошибка при обработке запроса. Попробуйте позже."
