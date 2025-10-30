from aiogram import Router, F
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    FSInputFile
)
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from services.analyzer import get_answer
from services.balance import get_balance
from services.stats import (
    save_user_query,
    get_user_stats,
    get_daily_stats,
    get_popular_queries,
    get_popular_sections,
    export_queries_to_excel,
    get_all_queries,
    get_all_users
)
from utils.logging import logger
import os

router = Router()


class StatsStates(StatesGroup):
    waiting_for_stats_period = State()
    waiting_for_export_period = State()


@router.message(Command("start"))
async def handle_start(message: Message):
    await message.answer(
        "👋 Привет! Я - умный помощник компании HRlink.\n\n"
        "Задайте мне любой вопрос о нашей компании, продуктах или услугах, "
        'и я постараюсь найти ответ в ''<u><b><a href="https://wiki.hr-link.ru/bin/view/Main/">базе знаний</a></b></u>.\n\n'
        "Обращайте внимание на <b><u>гиперссылки</u></b> в тексте ответа.\n"
        "В этих ссылках находится более полная статья по информации из базы знаний.\n\n"
        "<b>Просто пишите свой вопрос в чат!</b>\n\n"
        "Доступные команды:\n"
        "/help - справка\n"
        "/balance - баланс API\n"
        "/stats - статистика бота (только для администратора)"
    )


@router.message(Command("help"))
async def handle_help(message: Message):
    await message.answer(
        "ℹ️ Я могу ответить на вопросы о:\n\n"
        "- Наших продуктах и услугах\n"
        "- Условиях внедрения\n"
        "- Контактах компании\n"
        "- Технических характеристиках\n\n"
        'Все ответы берутся из <u><b><a href="https://wiki.hr-link.ru/bin/view/Main/">базы знаний</a></b></u>.\n\n'
        "<b>Доступные команды:</b>\n"
        "/start - начать работу\n"
        "/help - справка\n"
        "/balance - баланс API\n"
        "/stats - статистика бота (только для администратора)\n\n"
        "<b>Просто напишите ваш вопрос в чат!</b>"
    )


@router.message(Command("balance"))
async def handle_balance(message: Message):
    try:
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
                "Для пополнения баланса обратитесь к администратору бота."
            )
    except Exception as e:
        logger.error(f"Ошибка в обработчике баланса: {e}")
        await message.answer(
            "⚠️ Произошла внутренняя ошибка при проверке баланса.")


@router.message(Command("stats"))
async def handle_stats(message: Message):
    logger.info(f"Вызов /stats от пользователя {message.from_user.id}")
    try:
        if message.from_user.id != 281146928:  # Замените на ваш ID
            await message.answer(
                "❌ Эта команда доступна только администратору.")
            return

        stats = get_user_stats()
        daily_stats = get_daily_stats(7)
        popular_sections = get_popular_sections(5)  # ← Используем новую функцию

        response = "📊 <b>Статистика бота</b>\n\n"
        response += f"👥 Всего пользователей: <b>{stats['total_users']}</b>\n"
        response += f"📝 Всего запросов: <b>{stats['total_queries']}</b>\n"
        response += f"🔥 Активных пользователей (30 дней): <b>{stats['active_users']}</b>\n"
        response += f"📈 Среднее количество запросов на пользователя: <b>{stats['avg_queries_per_user']:.1f}</b>\n\n"

        response += "📅 <b>Статистика за 7 дней:</b>\n"
        for day in daily_stats:
            response += f"  {day['date']}: {day['total_queries']} запросов, {day['unique_users']} пользователей\n"

        response += "\n📚 <b>Популярные разделы:</b>\n"
        if popular_sections:
            for i, (section, count) in enumerate(popular_sections, 1):
                section_display = section[:50] + "..." if len(section) > 50 else section
                response += f"{i}. {section_display} ({count} запросов)\n"
        else:
            response += "📭 Разделы еще не анализировались\n"

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📊 Статистика за период",
                    callback_data="stats_period"),
                InlineKeyboardButton(
                    text="👥 Список пользователей",
                    callback_data="list_users"),
            ],
            [InlineKeyboardButton(
                text="📊 Выгрузить в Excel",
                callback_data="export_period")]
        ])

        await message.answer(response, reply_markup=keyboard)

    except Exception as e:
        logger.error(f"Ошибка показа статистики: {e}")
        await message.answer("❌ Ошибка при получении статистики.")


@router.callback_query(lambda c: c.data == "stats_period")
async def handle_stats_period(callback: CallbackQuery, state: FSMContext):
    await state.set_state(StatsStates.waiting_for_stats_period)
    await callback.message.answer(
        "📅 <b>Укажите период для статистики:</b>\n\n"
        "🔹 <code>1_day</code> — за 1 день\n"
        "🔹 <code>1_week</code> — за 1 неделю\n"
        "🔹 <code>1_month</code> — за 1 месяц\n"
        "🔹 <code>1_year</code> — за 1 год\n"
        "🔹 <code>дд.мм.гггг</code> — за конкретный день\n"
        "🔹 <code>мм.гггг</code> — за конкретный месяц\n"
        "🔹 <code>гггг</code> — за конкретный год\n\n"
        "Пример: <code>1_day</code>, <code>17.09.2025</code>, <code>09.2025</code>, <code>2025</code>"
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "export_period")
async def handle_export_period(callback: CallbackQuery, state: FSMContext):
    await state.set_state(StatsStates.waiting_for_export_period)
    await callback.message.answer(
        "📅 <b>Укажите период для выгрузки в Excel:</b>\n\n"
        "🔹 <code>1_day</code> — за 1 день\n"
        "🔹 <code>1_week</code> — за 1 неделю\n"
        "🔹 <code>1_month</code> — за 1 месяц\n"
        "🔹 <code>1_year</code> — за 1 год\n"
        "🔹 <code>дд.мм.гггг</code> — за конкретный день\n"
        "🔹 <code>мм.гггг</code> — за конкретный месяц\n"
        "🔹 <code>гггг</code> — за конкретный год\n\n"
        "Пример: <code>1_day</code>, <code>17.09.2025</code>, <code>09.2025</code>, <code>2025</code>"
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "list_users")
async def handle_list_users(callback: CallbackQuery):
    try:
        users = get_all_users()
        if not users:
            await callback.answer("❌ Пользователей не найдено.", show_alert=True)
            return
        response = "👥 <b>Список пользователей:</b>\n\n"
        for i, user in enumerate(users, 1):
            response += f"{i}. <b>ID:</b> {user['user_id']}\n"
            response += f"   <b>Имя:</b> {user['first_name'] or 'Не указано'}\n"
            response += f"   <b>Username:</b> @{user['username'] or 'Не указано'}\n"
            response += f"   <b>Всего запросов:</b> {user['total_queries']}\n\n"
        await callback.message.answer(response)
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка при получении списка пользователей: {e}")
        await callback.answer("❌ Произошла ошибка при получении списка пользователей.", show_alert=True)


@router.message(F.text & (
    F.text.startswith("1_day") |
    F.text.startswith("1_week") |
    F.text.startswith("1_month") |
    F.text.startswith("1_year") |
    F.text.regexp(r"^\d{2}\.\d{2}\.\d{4}$") |  # дд.мм.гггг
    F.text.regexp(r"^\d{2}\.\d{4}$") |         # мм.гггг
    F.text.regexp(r"^\d{4}$")                  # гггг
), StatsStates.waiting_for_export_period)
async def handle_export_period_request(message: Message, state: FSMContext):
    try:
        period = message.text.strip()
        # Создаем Excel файл
        file_path = export_queries_to_excel(period)
        
        if file_path and os.path.exists(file_path):
            # Отправляем файл пользователю
            file = FSInputFile(file_path)
            await message.answer_document(
                document=file,
                caption=f"📊 Выгрузка запросов за период: {period}"
            )
            # Удаляем временный файл
            os.remove(file_path)
        else:
            await message.answer("❌ Не удалось создать файл выгрузки или данные отсутствуют.")
            
    except Exception as e:
        logger.error(f"Ошибка при выгрузке в Excel: {e}")
        await message.answer("❌ Произошла ошибка при выгрузке данных.")
    
    await state.clear()


@router.message(F.text & (
    F.text.startswith("1_day") |
    F.text.startswith("1_week") |
    F.text.startswith("1_month") |
    F.text.startswith("1_year") |
    F.text.regexp(r"^\d{2}\.\d{2}\.\d{4}$") |  # дд.мм.гггг
    F.text.regexp(r"^\d{2}\.\d{4}$") |         # мм.гггг
    F.text.regexp(r"^\d{4}$")                  # гггг
), StatsStates.waiting_for_stats_period)
async def handle_stats_period_request(message: Message, state: FSMContext):
    period = message.text.strip()
    queries = get_all_queries(period)
    if not queries:
        await message.answer("❌ Запросов за этот период не найдено.")
        await state.clear()
        return
        
    page = 0
    queries_per_page = 5
    total_pages = (len(queries) + queries_per_page - 1) // queries_per_page
    
    response = f"📋 <b>Все запросы за {period}:</b>\n\n"
    start_index = page * queries_per_page
    end_index = min((page + 1) * queries_per_page, len(queries))
    
    for i, query in enumerate(queries[start_index:end_index], start_index + 1):
        response += f"{i}. <b>Пользователь:</b> {query['username'] or 'Без имени'}\n"
        response += f"   <b>Вопрос:</b> {query['question']}\n"
        response += f"   <b>Дата:</b> {query['created_at']}\n\n"
    
    if total_pages > 1:
        pagination_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="⬅️", callback_data=f"page_{period}_{page}_prev"),
                InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="ignore"),
                InlineKeyboardButton(text="➡️", callback_data=f"page_{period}_{page}_next"),
            ],
            [InlineKeyboardButton(text="🗑️ Закрыть", callback_data="close_queries")]
        ])
        await message.answer(response, reply_markup=pagination_keyboard)
    else:
        await message.answer(response)
    
    await state.clear()


@router.callback_query(lambda c: c.data.startswith("page_"))
async def handle_queries_pagination(callback: CallbackQuery):
    try:
        parts = callback.data.split("_")
        # Ожидаемый формат: page_1_day_0_next или page_17.09.2025_0_prev
        if len(parts) < 4:
            raise ValueError(f"Unexpected callback_data format: {callback.data}")
        
        # Извлекаем части
        period_parts = parts[1:-2]  # Все части между "page" и номером страницы
        period = "_".join(period_parts)
        page = int(parts[-2])
        action = parts[-1]
        
        queries = get_all_queries(period)
        if not queries:
            await callback.answer("❌ Запросов за этот период не найдено.", show_alert=True)
            return
            
        queries_per_page = 5
        total_pages = (len(queries) + queries_per_page - 1) // queries_per_page
        
        if action == "prev":
            page -= 1
        elif action == "next":
            page += 1
            
        if page < 0:
            page = 0
        elif page >= total_pages:
            page = total_pages - 1
            
        response = f"📋 <b>Все запросы за {period}:</b>\n\n"
        start_index = page * queries_per_page
        end_index = min((page + 1) * queries_per_page, len(queries))
        
        for i, query in enumerate(queries[start_index:end_index], start_index + 1):
            response += f"{i}. <b>Пользователь:</b> {query['username'] or 'Без имени'}\n"
            response += f"   <b>Вопрос:</b> {query['question']}\n"
            response += f"   <b>Дата:</b> {query['created_at']}\n\n"
            
        pagination_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="⬅️", callback_data=f"page_{period}_{page}_prev"),
                InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="ignore"),
                InlineKeyboardButton(text="➡️", callback_data=f"page_{period}_{page}_next"),
            ],
            [InlineKeyboardButton(text="🗑️ Закрыть", callback_data="close_queries")]
        ])
        
        await callback.message.edit_text(response, reply_markup=pagination_keyboard)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка при пагинации: {e}")
        await callback.answer("❌ Произошла ошибка при пагинации.", show_alert=True)




@router.callback_query(lambda c: c.data == "close_queries")
async def handle_close_queries(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer()


@router.message(F.text)
async def handle_question(message: Message):
    try:
        if len(message.text) < 3:
            await message.answer("Пожалуйста, задайте более развёрнутый вопрос.")
            return

        searching_text = '⏳ Ищу ответ, смотрю в <a href="https://wiki.hr-link.ru/bin/view/Main/">базе знаний</a>, ожидайте...'
        searching_msg = await message.answer(searching_text)
        await message.bot.send_chat_action(message.chat.id, "typing")
        answer, section = await get_answer(message.text)
        save_user_query(
            user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            question=message.text,
            answer=answer[:500] if answer else "Пустой ответ",
            section=section
        )
        await searching_msg.delete()
        await message.bot.send_chat_action(message.chat.id, "typing")
        await message.answer(answer)
    except Exception as e:
        logger.error(f"Ошибка обработки вопроса: {e}")
        await message.answer("Произошла ошибка при обработке вашего вопроса.")
