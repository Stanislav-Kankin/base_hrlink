import tiktoken
from pathlib import Path

encoding = tiktoken.encoding_for_model("gpt-4o")


def load_knowledge_base():
    """Загружает базу знаний из файла"""
    try:
        with open(Path(__file__).parent / 'base.txt', 'r', encoding='utf-8') as f:
            content = f.read()
            print("База знаний загружена успешно.")
            return content
    except Exception as e:
        print(f"Ошибка загрузки базы знаний: {e}")
        return ""


KNOWLEDGE_BASE = load_knowledge_base()

SYSTEM_PROMPT = f"""
Ты - интеллектуальный помощник-справочник компании HRlink.
Отвечай на вопросы, используя только предоставленную базу знаний.
Если информации нет в базе знаний, отвечай "Информация не найдена, уточните у менеджера".

Правила общения:
1. Будь вежливым и дружелюбным
2. Отвечай кратко (1-3 предложения)
3. Не придумывай информацию
4. На технические вопросы отвечай более подробно

База знаний компании:
{KNOWLEDGE_BASE}
"""
