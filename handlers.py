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
        'и я постараюсь найти ответ в <u><b><a href="https://wiki.hr-link.ru/bin/view/Main/">базе знаний</a></b></u>.\n\n'
        "Обращайте внимание на гиперссылки в тексте ответа.\n"
        "В этих ссылках находится более полная статься, по информации "
        "из которой берется информация.\n\n"
        "<b>Просто пишите свой вопрос в чат!</b>\n\n"
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
    """Обработчик команды для запроса текущего баланса"""
    try:
        # Показываем статус "печатает"
        await message.bot.send_chat_action(message.chat.id, "typing")

        balance = await get_balance()

        if balance is None:
            await message.answer(
                "❌ Не удалось получить баланс.\n\n"
                "Возможные причины:\n"
                "1. Не включено разрешение 'Запрос баланса' для API-ключа\n"
                "2. Проблемы с подключением к ProxyAPI\n"
                "3. Ошибка авторизации\n\n"
                "Проверьте настройки ключа в личном кабинете ProxyAPI."
            )
        else:
            await message.answer(
                f"💰 <b>Текущий баланс:</b> <code>{balance:.2f}</code> руб.\n\n"
                "Для пополнения баланса обратитесь к создаелю бота, "
                "или иному ответсвенному лицу."
            )

    except Exception as e:
        logger.error(f"Ошибка в обработчике баланса: {e}")
        await message.answer(
            "⚠️ Произошла внутренняя ошибка при проверке баланса"
            )


@router.message(F.text)
async def handle_question(message: Message):
    try:
        if len(message.text) < 3:
            await message.answer(
                "Пожалуйста, задайте более развернутый вопрос."
                )
            return
        searching_text = (
            '⏳ Ищу ответ, смотрю в <a href="https://wiki.hr-link.ru/bin/view/Main/">базе знаний</a>, ожидайте...'
            )
        # Отправляем сообщение с HTML-разметкой
        searching_msg = await message.answer(
            searching_text
            )

        await message.bot.send_chat_action(message.chat.id, "typing")
        answer = await get_answer(message.text)

        # Удаляем сообщение "Ищу ответ..." перед отправкой ответа
        await searching_msg.delete()
        await message.bot.send_chat_action(message.chat.id, "typing")
        await message.answer(answer)

    except Exception as e:
        logger.error(f"Ошибка обработки вопроса: {e}")
        await message.answer("Произошла ошибка при обработке вашего вопроса.")
