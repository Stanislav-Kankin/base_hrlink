from openai import AsyncOpenAI
from utils.logging import logger
from config import config
from services.classifier import classify_question
from services.knowledge_loader import load_section_knowledge
import asyncio

client = AsyncOpenAI(
    api_key=config.PROXY_API_KEY,
    base_url="https://api.proxyapi.ru/deepseek"
)

semaphore = asyncio.Semaphore(5)


async def get_answer(question: str) -> str:
    """Получает ответ на вопрос из базы знаний"""
    try:
        logger.info(f"Обработка вопроса: {question}")

        # Определяем раздел
        section = await classify_question(question)
        logger.info(f"Определен раздел: {section}")

        if not section:
            return (
                "Не удалось определить раздел для вопроса.\n\n"
                "Попробуйте использовать более"
                " конкретные формулировки, например:\n"
                "- Как добавить сотрудника в систему?\n"
                "- Как привязать электронную подпись?\n"
                "- Как загрузить документы массово?"
                )

        # Загружаем знания
        knowledge, file_path = load_section_knowledge(section)

        if not knowledge:
            # Пытаемся найти любой файл в разделе
            if '.' in section:
                main_section = section.split('.')[0] + '.'
                knowledge, file_path = load_section_knowledge(main_section)

            if not knowledge:
                return (
                    f"Раздел '{section}' временно недоступен.\n\n"
                    "Попробуйте:\n"
                    "1. Переформулировать вопрос\n"
                    "2. Обратиться в службу поддержки\n"
                    f"3. Проверить раздел {section} в базе знаний позже"
                    )

        # Формируем и отправляем запрос
        system_prompt = f"""Ты помощник компании HRlink.
          Отвечай на основе информации из раздела {section}.
Если информации недостаточно, предложи уточнить вопрос или
 обратиться в поддержку.
Правила общения:
    1. Будь вежливым и дружелюбным
    2. Отвечай развернуто на технические и юридические вопросы
    3. На простые вопросы отвечай кратко (1-3 предложения)
    4. Не придумывай информацию
    5. Если информации нет в базе знаний, отвечай:
       "Информация не найдена в разделе {section}.
         Уточните у менеджера или обратитесь в службу поддержки."

    7. Если вопрос требует информации из другого
      раздела, предложи уточнить раздел

    чтобы выделить текст жирным используй вместо * звездочки html теги <b>

Информация раздела:
{knowledge}"""

        response = await client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            temperature=0.3,
            max_tokens=10000
        )

        answer = response.choices[0].message.content
        return answer if answer else (
            "Не удалось найти ответ в базе знаний.\n"
            "Попробуйте задать вопрос более конкретно.")

    except Exception as e:
        logger.error(f"Ошибка обработки вопроса: {str(e)}")
        return (
            "Сервис временно недоступен.\n"
            "Пожалуйста, повторите попытку позже или обратитесь в поддержку."
            )
