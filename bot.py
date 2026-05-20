import os
import logging
from typing import Optional
import httpx
import asyncio

from aiogram import Bot, Dispatcher, Router, F, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from dotenv import load_dotenv

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Завантажуємо змінні оточення
load_dotenv()

# Ключові константи
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_BASE_URL = "http://127.0.0.1:8000"
ITEMS_PER_PAGE = 5

# Ініціалізуємо бота
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()
dp.include_router(router)

# HTTP клієнт з таймаутом для довгих запитів до Gemini API (10-15 сек)
client = httpx.AsyncClient(base_url=API_BASE_URL, timeout=30.0)

# Глобальний словник для збереження дисциплін (ключ: user_id, значення: відфільтрований список)
user_disciplines_cache = {}


# ==================== CALLBACK DATA ====================

class DisciplinesPaginationCallback(CallbackData, prefix="disciplines"):
    """Callback для пагінації дисциплін"""
    page: int
    user_id: int


# ==================== FSM СТАНИ ====================

class RegistrationStates(StatesGroup):
    """Стани для реєстрації студента"""
    waiting_for_name = State()
    waiting_for_course_year = State()
    waiting_for_specialty = State()


class CurriculumStates(StatesGroup):
    """Стани для генерації навчальної програми"""
    waiting_for_prompt = State()


# ==================== ФУНКЦІЇ-ДОПОМІЖНИКИ ====================

def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Створює головне меню"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📚 Доступні дисципліни")],
            [KeyboardButton(text="👤 Мій акаунт")],
            [KeyboardButton(text="🤖 Згенерувати програму")],
            [KeyboardButton(text="🔄 Змінити дані")]
        ],
        resize_keyboard=True
    )


def get_disciplines_page(disciplines: list, page: int) -> tuple[str, InlineKeyboardMarkup]:
    """
    Генерує текст та кнопки для однієї сторінки дисциплін
    
    Args:
        disciplines: Список дисциплін
        page: Номер сторінки (починаючи з 0)
        
    Returns:
        tuple: (текст, inline_keyboard)
    """
    total_pages = (len(disciplines) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    
    # Обчислюємо індекси для поточної сторінки
    start_idx = page * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    page_items = disciplines[start_idx:end_idx]
    
    # Генеруємо текст
    text = f"📚 <b>Доступні дисципліни</b> (сторінка {page + 1}/{total_pages})\n\n"
    for i, d in enumerate(page_items, start=start_idx + 1):
        text += (
            f"<b>{i}. {d['title']}</b>\n"
            f"   Викладач: {d['instructor_name']}\n"
            f"   Опис: {d['description'] or 'Немає опису'}\n"
            f"   Кредити: {d['credits']}\n\n"
        )
    
    # Генеруємо кнопки навігації окремих рядків
    keyboard_rows = []
    
    # Ряд 1: Назад | Вперед
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data=DisciplinesPaginationCallback(page=page - 1, user_id=0).pack()
        ))
    
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(
            text="Вперед ➡️",
            callback_data=DisciplinesPaginationCallback(page=page + 1, user_id=0).pack()
        ))
    
    if nav_buttons:
        keyboard_rows.append(nav_buttons)
    
    # Ряд 2: Меню
    keyboard_rows.append([InlineKeyboardButton(text="🏠 Меню", callback_data="back_to_menu")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
    
    return text, keyboard


async def get_student_by_telegram_id(telegram_id: str) -> Optional[dict]:
    """Отримує дані студента з API"""
    try:
        # Робимо запит через GET /students/ та перевіряємо вручну
        # Примітка: потім додамо спеціальний ендпоінт
        response = await client.get(f"/students/by-telegram/{telegram_id}")
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        logger.error(f"Error fetching student: {e}")
        return None


async def create_student(telegram_id: str, name: str, course_year: int, specialty: str) -> Optional[dict]:
    """Створює студента через API"""
    try:
        data = {
            "telegram_id": telegram_id,
            "name": name,
            "current_course_year": course_year,
            "specialty": specialty,
            "learning_preferences": None
        }
        response = await client.post("/students/", json=data)
        if response.status_code == 200:
            return response.json()
        logger.error(f"Failed to create student: {response.text}")
        return None
    except Exception as e:
        logger.error(f"Error creating student: {e}")
        return None


async def get_disciplines() -> Optional[list]:
    """Отримує список дисциплін"""
    try:
        response = await client.get("/disciplines/")
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        logger.error(f"Error fetching disciplines: {e}")
        return None


async def generate_curriculum(student_id: int, prompt_text: str) -> Optional[dict]:
    """Генерує навчальну програму"""
    try:
        # Переконуємось, що формат даних правильний
        payload = {"prompt_text": prompt_text}
        logger.info(f"Sending curriculum request with payload: {payload}")
        
        response = await client.post(
            f"/students/{student_id}/generate-curriculum",
            json=payload
        )
        
        logger.info(f"API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to generate curriculum: Status {response.status_code}, Response: {response.text}")
            return None
    except Exception as e:
        logger.error(f"Error generating curriculum: {e}")
        return None


# ==================== ОБРОБНИКИ КОМАНД ====================

@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    """Обробник команди /start"""
    telegram_id = str(message.from_user.id)
    
    # Перевіряємо чи студент вже зареєстрований
    student = await get_student_by_telegram_id(telegram_id)
    
    if student:
        # Студент вже зареєстрований
        await message.answer(
            f"👋 Вітаємо, {student['name']}!\n\n"
            f"Ви зареєстровані як студент {student['current_course_year']} курсу спеціальності '{student['specialty']}'.\n\n"
            f"Виберіть дію:",
            reply_markup=get_main_keyboard()
        )
    else:
        # Стартуємо реєстрацію
        await message.answer(
            "👋 Вітаємо! Здається, ви ще не зареєстровані.\n\n"
            "Давайте почнемо реєстрацію. Введіть своє ім'я:",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(RegistrationStates.waiting_for_name)
        # Зберігаємо telegram_id в стані
        await state.update_data(telegram_id=telegram_id)


@router.message(RegistrationStates.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    """Обробник введення імені"""
    await state.update_data(name=message.text)
    await message.answer("Введіть курс (1-4):")
    await state.set_state(RegistrationStates.waiting_for_course_year)


@router.message(RegistrationStates.waiting_for_course_year)
async def process_course_year(message: types.Message, state: FSMContext):
    """Обробник введення курсу"""
    try:
        course_year = int(message.text)
        if 1 <= course_year <= 4:
            await state.update_data(course_year=course_year)
            await message.answer("Введіть спеціальність (наприклад, 'Комп'ютерна наука', 'Математика'):")
            await state.set_state(RegistrationStates.waiting_for_specialty)
        else:
            await message.answer("❌ Будь ласка, введіть число від 1 до 4:")
    except ValueError:
        await message.answer("❌ Будь ласка, введіть число:")


@router.message(RegistrationStates.waiting_for_specialty)
async def process_specialty(message: types.Message, state: FSMContext):
    """Обробник введення спеціальності"""
    await state.update_data(specialty=message.text)
    
    # Отримуємо дані з FSM
    data = await state.get_data()
    
    # Реєструємо студента
    student = await create_student(
        telegram_id=data['telegram_id'],
        name=data['name'],
        course_year=data['course_year'],
        specialty=data['specialty']
    )
    
    if student:
        await message.answer(
            f"✅ Реєстрація успішна!\n\n"
            f"Ім'я: {student['name']}\n"
            f"Курс: {student['current_course_year']}\n"
            f"Спеціальність: {student['specialty']}\n\n"
            f"Виберіть дію:",
            reply_markup=get_main_keyboard()
        )
        await state.clear()
    else:
        await message.answer("❌ Помилка при реєстрації. Спробуйте ще раз.")
        await state.clear()


# ==================== ОБРОБНИКИ КНОПОК ====================

@router.message(F.text == "👤 Мій акаунт")
async def show_account(message: types.Message):
    """Показує дані акаунту студента"""
    telegram_id = str(message.from_user.id)
    student = await get_student_by_telegram_id(telegram_id)
    
    if student:
        account_text = (
            f"👤 <b>Ваш акаунт</b>\n\n"
            f"<b>Ім'я:</b> {student['name']}\n"
            f"<b>Курс:</b> {student['current_course_year']}\n"
            f"<b>Спеціальність:</b> {student['specialty']}\n"
            f"<b>ID:</b> {student['id']}\n"
        )
        if student.get('learning_preferences'):
            account_text += f"<b>Побажання:</b> {student['learning_preferences']}\n"
        
        await message.answer(account_text, parse_mode="HTML", reply_markup=get_main_keyboard())
    else:
        await message.answer("❌ Студента не знайдено. Виконайте /start для реєстрації.")


@router.message(F.text == "📚 Доступні дисципліни")
async def show_disciplines(message: types.Message):
    """Показує дисципліни відповідно до курсу та спеціальності студента (з пагінацією)"""
    telegram_id = str(message.from_user.id)
    student = await get_student_by_telegram_id(telegram_id)
    
    if not student:
        await message.answer("❌ Студента не знайдено. Виконайте /start для реєстрації.")
        return
    
    # Отримуємо всі дисципліни
    disciplines = await get_disciplines()
    
    if not disciplines:
        await message.answer("❌ Не вдалося завантажити дисципліни.")
        return
    
    # Фільтруємо дисципліни за курсом та спеціальністю
    filtered = [d for d in disciplines 
                if d.get('course_year') == student['current_course_year'] and 
                   (d.get('specialty') == student['specialty'] or d.get('specialty') == 'General')]
    
    if not filtered:
        # Показуємо всі дисципліни, якщо немає підходящих
        filtered = disciplines
    
    # Зберігаємо в кеш
    user_disciplines_cache[telegram_id] = filtered
    
    # Генеруємо першу сторінку
    text, keyboard = get_disciplines_page(filtered, 0)
    
    await message.answer(text, parse_mode="HTML", reply_markup=keyboard)


@router.callback_query(DisciplinesPaginationCallback.filter())
async def disciplines_pagination(callback: types.CallbackQuery, callback_data: DisciplinesPaginationCallback):
    """Обробляє навігацію по сторінках дисциплін"""
    telegram_id = str(callback.from_user.id)
    page = callback_data.page
    
    logger.info(f"[PAGINATION] User {telegram_id} requested page {page}")
    
    # Перевіряємо, що callback має message
    if not callback.message:
        logger.error(f"[PAGINATION] No message object in callback from user {telegram_id}")
        await callback.answer("❌ Помилка: не вдалося оновити повідомлення.", show_alert=True)
        return
    
    # Отримуємо дисципліни з кешу
    if telegram_id not in user_disciplines_cache:
        logger.warning(f"[PAGINATION] Cache miss for user {telegram_id}. Session expired.")
        await callback.answer("❌ Сесія дисциплін закінчилась. Спробуйте ще раз.", show_alert=True)
        return
    
    disciplines = user_disciplines_cache[telegram_id]
    logger.info(f"[PAGINATION] Retrieved {len(disciplines)} cached disciplines for user {telegram_id}")
    
    try:
        # Генеруємо текст та клавіатуру для сторінки
        text, keyboard = get_disciplines_page(disciplines, page)
        logger.info(f"[PAGINATION] Generated page {page} for user {telegram_id}")
        
        # Оновлюємо повідомлення
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
        logger.info(f"[PAGINATION] Successfully updated message for user {telegram_id}, page {page}")
        
        # Завжди відповідаємо на callback (без alert)
        await callback.answer()
    except Exception as e:
        logger.error(f"[PAGINATION] Error updating message for user {telegram_id}: {e}", exc_info=True)
        await callback.answer("❌ Помилка при оновленні сторінки. Спробуйте ще раз.", show_alert=True)


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery):
    """Повертає до головного меню"""
    await callback.message.delete()
    await callback.message.answer(
        "Виберіть дію:",
        reply_markup=get_main_keyboard()
    )
    await callback.answer()



@router.message(F.text == "🤖 Згенерувати програму")
async def start_curriculum_generation(message: types.Message, state: FSMContext):
    """Стартує генерацію навчальної програми"""
    telegram_id = str(message.from_user.id)
    student = await get_student_by_telegram_id(telegram_id)
    
    if not student:
        await message.answer("❌ Студента не знайдено. Виконайте /start для реєстрації.")
        return
    
    await message.answer(
        "🤖 Введіть ваші побажання щодо навчальної програми:\n"
        "(Наприклад: 'Я хочу дисципліни з практичними заняттями, сфокусовані на програмуванні')",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(CurriculumStates.waiting_for_prompt)
    await state.update_data(student_id=student['id'])


@router.message(CurriculumStates.waiting_for_prompt)
async def process_curriculum_prompt(message: types.Message, state: FSMContext):
    """Обробляє побажання та генерує програму"""
    data = await state.get_data()
    student_id = data['student_id']
    telegram_id = str(message.from_user.id)
    
    logger.info(f"[CURRICULUM] User {telegram_id} requested curriculum generation")
    logger.debug(f"[CURRICULUM] Prompt: {message.text[:100]}...")
    
    await message.answer("⏳ Генерую вашу навчальну програму... Будь ласка, чекайте. Це може зайняти 15-30 секунд.")
    
    try:
        # Генеруємо програму
        logger.info(f"[CURRICULUM] Calling API for student_id={student_id}")
        result = await generate_curriculum(student_id, message.text)
        
        if result:
            logger.info(f"[CURRICULUM] Successfully generated curriculum for user {telegram_id}")
            
            # Формуємо відповідь
            response_text = f"🎓 <b>Ваша персоналізована програма навчання</b>\n\n"
            
            # Додаємо загальний звіт
            response_text += f"<b>📋 Загальна рекомендація:</b>\n{result['general_report']}\n\n"
            
            # Додаємо рекомендовані дисципліни
            response_text += f"<b>📚 Рекомендовані дисципліни:</b>\n"
            for i, rec in enumerate(result['recommendations'], 1):
                response_text += (
                    f"\n<b>{i}. {rec['discipline']['title']}</b>\n"
                    f"   Викладач: {rec['discipline']['instructor_name']}\n"
                    f"   Кредити: {rec['discipline']['credits']}\n"
                    f"   <b>Обґрунтування:</b> {rec['match_reason']}\n"
                )
            
            response_text += f"\n<b>Усього кредитів:</b> {result['total_credits']}"
            
            logger.info(f"[CURRICULUM] Sending response to user {telegram_id}: {len(result['recommendations'])} recommendations, {result['total_credits']} credits")
            await message.answer(response_text, parse_mode="HTML", reply_markup=get_main_keyboard())
        else:
            logger.error(f"[CURRICULUM] API returned None for user {telegram_id}")
            await message.answer(
                "❌ Помилка при генерації програми. Спробуйте ще раз пізніше.",
                reply_markup=get_main_keyboard()
            )
    except Exception as e:
        logger.error(f"[CURRICULUM] Error generating curriculum for user {telegram_id}: {e}", exc_info=True)
        
        # Формуємо детальне повідомлення про помилку для користувача
        error_msg = str(e)
        if "400" in error_msg:
            user_message = "❌ Помилка: API повернув невалідний відповідь. Спробуйте переформулювати ваше прохання."
        elif "500" in error_msg or "timeout" in error_msg.lower():
            user_message = "❌ Помилка сервера або таймаут. Спробуйте ще раз через кілька хвилин."
        else:
            user_message = f"❌ Помилка: {error_msg}"
        
        logger.error(f"[CURRICULUM] Sending error message to user {telegram_id}: {user_message}")
        await message.answer(user_message, reply_markup=get_main_keyboard())
    
    await state.clear()


@router.message(F.text == "🔄 Змінити дані")
async def change_data(message: types.Message, state: FSMContext):
    """Стартує процес зміни даних"""
    telegram_id = str(message.from_user.id)
    student = await get_student_by_telegram_id(telegram_id)
    
    if not student:
        await message.answer("❌ Студента не знайдено. Виконайте /start для реєстрації.")
        return
    
    await message.answer(
        "⚠️ Функція змінення даних буде реалізована пізніше.\n\n"
        f"Поточні дані:\n"
        f"Ім'я: {student['name']}\n"
        f"Курс: {student['current_course_year']}\n"
        f"Спеціальність: {student['specialty']}",
        reply_markup=get_main_keyboard()
    )


# ==================== ОБРОБНИК ДЛЯ НЕВІДОМИХ ПОВІДОМЛЕНЬ ====================

@router.message()
async def echo(message: types.Message):
    """Обробляє невідомі повідомлення"""
    await message.answer(
        "❓ Я не розумію цієї команди. Виберіть одну з кнопок меню:",
        reply_markup=get_main_keyboard()
    )


# ==================== ЗАПУСК БОТА ====================

async def main():
    """Головна функція"""
    # Удалення попередніх webhook'ів
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Запуск polling
    logger.info("Bot started polling...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
