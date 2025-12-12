from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from datetime import datetime, timedelta
import logging

from bot.utils.states import MasterStates
from bot.keyboards.inline import cancel_keyboard

router = Router()
logger = logging.getLogger(__name__)

def is_master(user_id: int, crud) -> bool:
    """Проверка что пользователь является мастером"""
    master = crud.get_master_by_telegram_id(user_id)
    return master is not None

@router.message(Command("master"))
async def cmd_master(message: Message, crud):
    """Панель мастера"""
    
    if not is_master(message.from_user.id, crud):
        await message.answer("⛔ У вас нет доступа к этой команде")
        return
    
    # Получаем информацию о мастере
    master = await crud.get_master_by_telegram_id(message.from_user.id)
    
    # Получаем статистику мастера
    appointments = await crud.get_master_appointments(master['id'])
    
    pending_count = sum(1 for a in appointments if a['status'] == 'pending')
    today_count = sum(1 for a in appointments if a['start_time'].date() == datetime.now().date())
    
    stats_text = f"""
👩‍🔧 Панель мастера: {master['full_name']}

📊 Статистика:
• Всего записей: {len(appointments)}
• Ожидают подтверждения: {pending_count}
• Записей сегодня: {today_count}

Выберите действие:
    """
    
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="📋 Мои записи", callback_data="master_appointments"),
        InlineKeyboardButton(text="⏳ Ожидают подтверждения", callback_data="master_pending"),
        InlineKeyboardButton(text="📅 Расписание", callback_data="master_schedule"),
        InlineKeyboardButton(text="⚙️  Настройки", callback_data="master_settings")
    )
    builder.adjust(2)
    
    await message.answer(stats_text, reply_markup=builder.as_markup())

@router.callback_query(F.data == "master_appointments")
async def show_master_appointments(callback: CallbackQuery, crud):
    """Показать записи мастера"""
    
    await callback.answer()
    
    master = await crud.get_master_by_telegram_id(callback.from_user.id)
    if not master:
        await callback.answer("❌ Вы не являетесь мастером")
        return
    
    appointments = await crud.get_master_appointments(master['id'])
    
    if appointments:
        appointments_text = ""
        for app in appointments[:10]:  # Показываем последние 10 записей
            status_icons = {
                'pending': '⏳',
                'confirmed': '✅',
                'completed': '🎉',
                'cancelled': '❌'
            }
            
            appointments_text += f"""
{status_icons.get(app['status'], '📝')} #{app['id']}
👤 {app['client_name'] or 'Клиент'}
💆 {app['service_name']}
📅 {app['start_time'].strftime('%d.%m.%Y %H:%M')}
🔄 {app['status']}
            """
        
        text = f"📋 Ваши записи:\n{appointments_text}"
        
        builder = InlineKeyboardBuilder()
        builder.add(
            InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_master"),
            InlineKeyboardButton(text="⏳ Ожидают", callback_data="master_pending")
        )
        
        await callback.message.edit_text(text, reply_markup=builder.as_markup())
    else:
        text = "📭 У вас пока нет записей"
        
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_master"))
        
        await callback.message.edit_text(text, reply_markup=builder.as_markup())

@router.callback_query(F.data == "master_pending")
async def show_pending_appointments(callback: CallbackQuery, crud):
    """Показать записи ожидающие подтверждения"""
    
    await callback.answer()
    
    master = await crud.get_master_by_telegram_id(callback.from_user.id)
    if not master:
        await callback.answer("❌ Вы не являетесь мастером")
        return
    
    appointments = await crud.get_master_appointments(master['id'], status='pending')
    
    if appointments:
        appointments_text = ""
        builder = InlineKeyboardBuilder()
        
        for app in appointments[:5]:  # Показываем до 5 записей
            appointments_text += f"""
⏳ Запись #{app['id']}
👤 {app['client_name'] or 'Клиент'}
💆 {app['service_name']}
📅 {app['start_time'].strftime('%d.%m.%Y %H:%M')}
            """
            
            # Добавляем кнопки для подтверждения/отклонения
            builder.add(
                InlineKeyboardButton(
                    text=f"✅ Подтвердить #{app['id']}",
                    callback_data=f"confirm_{app['id']}"
                ),
                InlineKeyboardButton(
                    text=f"❌ Отклонить #{app['id']}",
                    callback_data=f"reject_{app['id']}"
                )
            )
        
        builder.add(InlineKeyboardButton(text="◀️ Назад", callback_data="master_appointments"))
        builder.adjust(1)
        
        text = f"⏳ Записи ожидающие подтверждения:\n{appointments_text}"
        await callback.message.edit_text(text, reply_markup=builder.as_markup())
    else:
        text = "✅ Нет записей ожидающих подтверждения"
        
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(text="◀️ Назад", callback_data="master_appointments"))
        
        await callback.message.edit_text(text, reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("confirm_"))
async def confirm_appointment(callback: CallbackQuery, crud):
    """Подтвердить запись"""
    
    await callback.answer()
    
    appointment_id = int(callback.data.split("_")[1])
    master = await crud.get_master_by_telegram_id(callback.from_user.id)
    
    if not master:
        await callback.answer("❌ Вы не являетесь мастером")
        return
    
    success = await crud.update_appointment_status(appointment_id, master['id'], 'confirmed')
    
    if success:
        # Получаем детали записи для уведомления клиента
        appointment = await crud.get_appointment_details(appointment_id)
        
        # TODO: Отправить уведомление клиенту
        
        await callback.answer("✅ Запись подтверждена")
        
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(text="◀️ Назад к записям", callback_data="master_pending"))
        
        await callback.message.edit_text(
            f"✅ Запись #{appointment_id} подтверждена!\n\n"
            f"Клиент: {appointment['client_name']}\n"
            f"Дата: {appointment['start_time'].strftime('%d.%m.%Y %H:%M')}\n"
            f"Услуга: {appointment['service_name']}",
            reply_markup=builder.as_markup()
        )
    else:
        await callback.answer("❌ Ошибка подтверждения")

@router.callback_query(F.data.startswith("reject_"))
async def reject_appointment(callback: CallbackQuery, crud):
    """Отклонить запись"""
    
    await callback.answer()
    
    appointment_id = int(callback.data.split("_")[1])
    master = await crud.get_master_by_telegram_id(callback.from_user.id)
    
    if not master:
        await callback.answer("❌ Вы не являетесь мастером")
        return
    
    success = await crud.update_appointment_status(appointment_id, master['id'], 'cancelled')
    
    if success:
        await callback.answer("❌ Запись отклонена")
        
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(text="◀️ Назад к записям", callback_data="master_pending"))
        
        await callback.message.edit_text(
            f"❌ Запись #{appointment_id} отклонена",
            reply_markup=builder.as_markup()
        )
    else:
        await callback.answer("❌ Ошибка отклонения")

@router.callback_query(F.data == "back_to_master")
async def back_to_master_panel(callback: CallbackQuery):
    """Вернуться в панель мастера"""
    
    await callback.answer()
    await cmd_master(callback.message, callback.bot['crud'])