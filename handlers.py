from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from services.analyzer import get_answer
from services.balance import get_balance
from utils.logging import logger

router = Router()


@router.message(Command("start"))
async def handle_start(message: Message):
    await message.answer(
        "👋 Привет! Я - умный помощник компании HRlink.\n\n"
        "Задайте мне любой вопрос о нашей компании, продуктах или услугах, "
        "и я постараюсь найти ответ в базе знаний.\n\n"
        "Доступные команды:\n"
        "/help - справка\n"
        "/balance - баланс API"
    )


@router.message(Command("help"))
async def handle_help(message: Message):
    await message.answer(
        "ℹ️ Я могу ответить на вопросы о:\n"
        "- Наших продуктах и услугах\n"
        "- Условиях внедрения\n"
        "- Контактах компании\n"
        "- Технических характеристиках\n\n"
        "Просто напишите ваш вопрос в чат!"
    )


@router.message(Command("balance"))
async def handle_balance(message: Message):
    balance = await get_balance()
    if balance is None:
        await message.answer("Не удалось проверить баланс API")
    else:
        await message.answer(f"💰 Текущий баланс API: {balance} руб.")


@router.message(F.text)
async def handle_question(message: Message):
    try:
        if len(message.text) < 3:
            await message.answer(
                "Пожалуйста, задайте более развернутый вопрос."
                )
            return

        await message.bot.send_chat_action(message.chat.id, "typing")
        answer = await get_answer(message.text)
        await message.answer(answer)

    except Exception as e:
        logger.error(f"Ошибка обработки вопроса: {e}")
        await message.answer("Произошла ошибка при обработке вашего вопроса.")
