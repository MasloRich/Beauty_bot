from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext

from bot.utils.states import AdminStates
from bot.keyboards.inline import admin_menu_keyboard, yes_no_keyboard
from config import Config

import logging

router = Router()
logger = logging.getLogger(__name__)
config = Config()

# Фильтр для проверки администратора
def is_admin(user_id: int) -> bool:
    return user_id in config.ADMIN_IDS

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    """Панель администратора"""
    
    if not is_admin(message.from_user.id):
        await message.answer("⛔ У вас нет доступа к этой команде")
        return
    
    await message.answer(
        "👨‍💼 Панель администратора",
        reply_markup=admin_menu_keyboard()
    )

@router.callback_query(F.data == "admin_stats")
async def show_admin_stats(callback: CallbackQuery):
    """Показать статистику"""
    
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа")
        return
    
    await callback.answer()
    
    # TODO: Получить статистику из БД
    stats_text = """
📊 Статистика за сегодня (15.01.2024):

👥 Клиенты:
• Новые клиенты: 5
• Всего клиентов: 127

📅 Записи:
• Записей сегодня: 12
• Подтверждено: 10
• Ожидают подтверждения: 2

💰 Финансы:
• Выручка за день: 25,000 руб.
• Средний чек: 2,083 руб.

👩‍🔧 Мастера:
• Самый популярный мастер: Анна (6 записей)
• Самая популярная услуга: Наращивание ресниц
    """
    
    await callback.message.edit_text(stats_text, reply_markup=admin_menu_keyboard())