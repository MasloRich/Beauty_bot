from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def main_menu_keyboard():
    """Главное меню для клиентов"""
    builder = InlineKeyboardBuilder()
    
    builder.add(
        InlineKeyboardButton(text="📅 Записаться", callback_data="book_appointment"),
        InlineKeyboardButton(text="📋 Мои записи", callback_data="my_appointments"),
        InlineKeyboardButton(text="ℹ️  О студии", callback_data="about_studio"),
        InlineKeyboardButton(text="📞 Контакты", callback_data="contacts")
    )
    
    builder.adjust(2, 1, 1)
    return builder.as_markup()

def cancel_keyboard():
    """Клавиатура для отмены действия"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="❌ Отмена", callback_data="cancel"))
    return builder.as_markup()

def masters_list_keyboard(masters):
    """Список мастеров для выбора"""
    builder = InlineKeyboardBuilder()
    
    for master in masters:
        builder.add(InlineKeyboardButton(
            text=f"{master['full_name']} ({master['experience']})",
            callback_data=f"master_{master['id']}"
        ))
    
    builder.add(InlineKeyboardButton(text="❌ Отмена", callback_data="cancel"))
    builder.adjust(1)
    return builder.as_markup()

def yes_no_keyboard():
    """Клавиатура Да/Нет"""
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="✅ Да", callback_data="yes"),
        InlineKeyboardButton(text="❌ Нет", callback_data="no")
    )
    return builder.as_markup()

def admin_menu_keyboard():
    """Меню администратора"""
    builder = InlineKeyboardBuilder()
    
    builder.add(
        InlineKeyboardButton(text="👥 Мастера", callback_data="admin_masters"),
        InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats"),
        InlineKeyboardButton(text="📅 Все записи", callback_data="admin_bookings"),
        InlineKeyboardButton(text="💰 Финансы", callback_data="admin_finance")
    )
    
    builder.adjust(2, 2)
    return builder.as_markup()

def back_to_main_keyboard():
    """Клавиатура для возврата в главное меню"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🏠 В главное меню", callback_data="main_menu"))
    return builder.as_markup()