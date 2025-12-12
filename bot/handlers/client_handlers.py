from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from datetime import datetime, timedelta
import logging

from bot.utils.states import ClientStates
from bot.keyboards.inline import (
    main_menu_keyboard, 
    cancel_keyboard, 
    masters_list_keyboard,
    yes_no_keyboard
)

router = Router()
logger = logging.getLogger(__name__)

# Временное хранилище записей (позже заменим на БД)
user_appointments = {}

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    logger.info(f"👤 Пользователь {user_id} ({user_name}) запустил бота")
    
    welcome_text = f"""
👋 Привет, {user_name}!

Добро пожаловать в студию красоты!

✨ Мы предлагаем:
• Наращивание ресниц
• Ламинирование ресниц
• Коррекция бровей
• Оформление бровей

Выберите действие:
    """
    
    await message.answer(welcome_text, reply_markup=main_menu_keyboard())

@router.callback_query(F.data == "book_appointment")
async def start_booking(callback: CallbackQuery, state: FSMContext):
    """Начало процесса записи"""
    
    await callback.answer()
    await callback.message.edit_text(
        "Выберите мастера:",
        reply_markup=masters_list_keyboard([
            {"id": 1, "full_name": "Анна", "experience": "5 лет"},
            {"id": 2, "full_name": "Мария", "experience": "3 года"},
            {"id": 3, "full_name": "Елена", "experience": "7 лет"}
        ])
    )
    
    await state.set_state(ClientStates.choosing_master)

@router.callback_query(F.data.startswith("master_"))
async def choose_master(callback: CallbackQuery, state: FSMContext):
    """Выбор мастера"""
    
    await callback.answer()
    master_id = callback.data.split("_")[1]
    
    # Сохраняем выбранного мастера в состоянии
    await state.update_data(master_id=master_id)
    
    # TODO: Получить услуги мастера из БД
    services = [
        {"id": 1, "name": "Наращивание ресниц", "price": 2500, "duration": "2 часа"},
        {"id": 2, "name": "Ламинирование ресниц", "price": 2000, "duration": "1.5 часа"},
        {"id": 3, "name": "Коррекция бровей", "price": 1500, "duration": "1 час"},
        {"id": 4, "name": "Оформление бровей", "price": 1200, "duration": "45 минут"},
    ]
    
    # Создаем клавиатуру с услугами
    builder = InlineKeyboardBuilder()
    for service in services:
        builder.add(InlineKeyboardButton(
            text=f"{service['name']} - {service['price']} руб.",
            callback_data=f"service_{service['id']}"
        ))
    
    builder.add(InlineKeyboardButton(text="❌ Отмена", callback_data="cancel"))
    builder.adjust(1)
    
    await callback.message.edit_text(
        "Выберите услугу:",
        reply_markup=builder.as_markup()
    )
    
    await state.set_state(ClientStates.choosing_service)

@router.callback_query(F.data.startswith("service_"))
async def choose_service(callback: CallbackQuery, state: FSMContext):
    """Выбор услуги"""
    
    await callback.answer()
    service_id = callback.data.split("_")[1]
    
    # TODO: Получить информацию об услуге из БД
    services_info = {
        "1": {"name": "Наращивание ресниц", "price": 2500, "duration": "2 часа"},
        "2": {"name": "Ламинирование ресниц", "price": 2000, "duration": "1.5 часа"},
        "3": {"name": "Коррекция бровей", "price": 1500, "duration": "1 час"},
        "4": {"name": "Оформление бровей", "price": 1200, "duration": "45 минут"},
    }
    
    service_info = services_info.get(service_id)
    
    if not service_info:
        await callback.answer("❌ Услуга не найдена")
        return
    
    # Сохраняем информацию об услуге в состоянии
    await state.update_data(
        service_id=service_id,
        service_name=service_info["name"],
        service_price=service_info["price"],
        service_duration=service_info["duration"]
    )
    
    # Генерируем даты на ближайшие 7 дней
    dates = []
    today = datetime.now()
    for i in range(1, 8):
        date = today + timedelta(days=i)
        if date.weekday() < 5:  # Только будние дни (0-4 = пн-пт)
            dates.append(date.strftime("%d.%m.%Y"))
    
    # Создаем клавиатуру с датами
    builder = InlineKeyboardBuilder()
    for date in dates:
        builder.add(InlineKeyboardButton(
            text=date,
            callback_data=f"date_{date}"
        ))
    
    builder.add(InlineKeyboardButton(text="❌ Отмена", callback_data="cancel"))
    builder.adjust(2)
    
    await callback.message.edit_text(
        f"✅ Вы выбрали: {service_info['name']}\n\n"
        "Выберите дату:",
        reply_markup=builder.as_markup()
    )
    
    await state.set_state(ClientStates.choosing_date)

@router.callback_query(F.data.startswith("date_"))
async def choose_date(callback: CallbackQuery, state: FSMContext):
    """Выбор даты"""
    
    await callback.answer()
    date = callback.data.split("_")[1]
    
    # Сохраняем дату в состоянии
    await state.update_data(date=date)
    
    # TODO: Получить доступное время для мастера на эту дату из БД
    # Пока используем тестовые временные слоты
    time_slots = [
        "09:00", "10:30", "12:00", "13:30", 
        "15:00", "16:30", "18:00", "19:30"
    ]
    
    # Создаем клавиатуру со временем
    builder = InlineKeyboardBuilder()
    for time in time_slots:
        builder.add(InlineKeyboardButton(
            text=time,
            callback_data=f"time_{time}"
        ))
    
    builder.add(InlineKeyboardButton(text="◀️ Назад к датам", callback_data="back_to_dates"))
    builder.add(InlineKeyboardButton(text="❌ Отмена", callback_data="cancel"))
    builder.adjust(2)
    
    await callback.message.edit_text(
        f"📅 Вы выбрали дату: {date}\n\n"
        "Выберите время:",
        reply_markup=builder.as_markup()
    )
    
    await state.set_state(ClientStates.choosing_time)

@router.callback_query(F.data == "back_to_dates")
async def back_to_dates(callback: CallbackQuery, state: FSMContext):
    """Вернуться к выбору даты"""
    
    await callback.answer()
    await choose_service(callback, state)

@router.callback_query(F.data.startswith("time_"))
async def choose_time(callback: CallbackQuery, state: FSMContext):
    """Выбор времени"""
    
    await callback.answer()
    time = callback.data.split("_")[1]
    
    # Сохраняем время в состоянии
    await state.update_data(time=time)
    
    # Получаем все данные из состояния
    data = await state.get_data()
    
    confirmation_text = f"""
✅ Подтвердите запись:

👩‍🔧 Мастер: {get_master_name(data.get('master_id'))}
💆 Услуга: {data.get('service_name')}
💰 Стоимость: {data.get('service_price')} руб.
⏱️ Длительность: {data.get('service_duration')}
📅 Дата: {data.get('date')}
🕐 Время: {data.get('time')}

После подтверждения мастер получит уведомление.
Новые клиенты должны внести предоплату 500 руб.
    """
    
    # Создаем клавиатуру для подтверждения
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="✅ Подтвердить запись", callback_data="confirm_booking"),
        InlineKeyboardButton(text="◀️ Назад ко времени", callback_data="back_to_times"),
        InlineKeyboardButton(text="❌ Отменить", callback_data="cancel")
    )
    builder.adjust(1)
    
    await callback.message.edit_text(
        confirmation_text,
        reply_markup=builder.as_markup()
    )
    
    await state.set_state(ClientStates.confirming_booking)

@router.callback_query(F.data == "back_to_times")
async def back_to_times(callback: CallbackQuery, state: FSMContext):
    """Вернуться к выбору времени"""
    
    await callback.answer()
    data = await state.get_data()
    date = data.get('date')
    
    # Пересоздаем сообщение с выбором времени
    await choose_date(callback, state)

@router.callback_query(F.data == "confirm_booking")
async def confirm_booking(callback: CallbackQuery, state: FSMContext):
    """Подтверждение записи"""
    
    await callback.answer()
    
    # Получаем данные из состояния
    data = await state.get_data()
    user_id = callback.from_user.id
    
    # TODO: Сохранить запись в БД
    # Временно сохраняем в памяти
    if user_id not in user_appointments:
        user_appointments[user_id] = []
    
    appointment_id = len(user_appointments[user_id]) + 1
    appointment = {
        "id": appointment_id,
        "master_id": data.get('master_id'),
        "master_name": get_master_name(data.get('master_id')),
        "service_name": data.get('service_name'),
        "service_price": data.get('service_price'),
        "date": data.get('date'),
        "time": data.get('time'),
        "status": "pending",  # Ожидает подтверждения мастера
        "created_at": datetime.now().strftime("%d.%m.%Y %H:%M")
    }
    
    user_appointments[user_id].append(appointment)
    
    # TODO: Отправить уведомление мастеру
    
    booking_details = f"""
🎉 Запись #{appointment_id} подтверждена!

Детали записи:
• Мастер: {appointment['master_name']}
• Услуга: {appointment['service_name']}
• Дата: {appointment['date']}
• Время: {appointment['time']}
• Стоимость: {appointment['service_price']} руб.
• Статус: Ожидает подтверждения мастера

📱 Вы получите напоминание за 24 часа до визита.

Хорошего дня! ✨
    """
    
    # Клавиатура с действиями после записи
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="📋 Мои записи", callback_data="my_appointments"),
        InlineKeyboardButton(text="📅 Новая запись", callback_data="book_appointment"),
        InlineKeyboardButton(text="🏠 В главное меню", callback_data="main_menu")
    )
    builder.adjust(1)
    
    await callback.message.edit_text(
        booking_details,
        reply_markup=builder.as_markup()
    )
    
    # Очищаем состояние
    await state.clear()

@router.callback_query(F.data == "main_menu")
async def go_to_main_menu(callback: CallbackQuery):
    """Вернуться в главное меню"""
    
    await callback.answer()
    await cmd_start(callback.message)

@router.callback_query(F.data == "my_appointments")
async def show_my_appointments(callback: CallbackQuery):
    """Показать мои записи"""
    
    await callback.answer()
    user_id = callback.from_user.id
    
    appointments = user_appointments.get(user_id, [])
    
    if appointments:
        appointments_text = ""
        for appointment in appointments:
            status_icon = "⏳" if appointment['status'] == 'pending' else "✅"
            appointments_text += f"""
{status_icon} Запись #{appointment['id']}
📅 {appointment['date']} {appointment['time']}
👩‍🔧 {appointment['master_name']}
💆 {appointment['service_name']}
💰 {appointment['service_price']} руб.
🔄 Статус: {appointment['status']}
            """
        
        text = f"📋 Ваши записи:\n{appointments_text}"
        
        # Создаем клавиатуру с кнопками отмены для каждой записи
        builder = InlineKeyboardBuilder()
        for appointment in appointments:
            if appointment['status'] == 'pending':  # Можно отменять только ожидающие записи
                builder.add(InlineKeyboardButton(
                    text=f"❌ Отменить запись #{appointment['id']}",
                    callback_data=f"cancel_appointment_{appointment['id']}"
                ))
        
        builder.add(InlineKeyboardButton(text="🏠 В главное меню", callback_data="main_menu"))
        builder.adjust(1)
        
        await callback.message.edit_text(
            text,
            reply_markup=builder.as_markup()
        )
    else:
        text = "📭 У вас пока нет записей"
        
        builder = InlineKeyboardBuilder()
        builder.add(
            InlineKeyboardButton(text="📅 Записаться", callback_data="book_appointment"),
            InlineKeyboardButton(text="🏠 В главное меню", callback_data="main_menu")
        )
        builder.adjust(1)
        
        await callback.message.edit_text(
            text,
            reply_markup=builder.as_markup()
        )

@router.callback_query(F.data.startswith("cancel_appointment_"))
async def cancel_appointment(callback: CallbackQuery):
    """Отмена записи"""
    
    await callback.answer()
    
    user_id = callback.from_user.id
    appointment_id = int(callback.data.split("_")[2])
    
    # Находим запись для отмене
    if user_id in user_appointments:
        for i, appointment in enumerate(user_appointments[user_id]):
            if appointment['id'] == appointment_id:
                # Удаляем запись
                deleted_appointment = user_appointments[user_id].pop(i)
                
                # TODO: Отправить уведомление мастеру об отмене
                # TODO: Вернуть предоплату если была
                
                # Показываем подтверждение отмены
                builder = InlineKeyboardBuilder()
                builder.add(
                    InlineKeyboardButton(text="📋 Мои записи", callback_data="my_appointments"),
                    InlineKeyboardButton(text="🏠 В главное меню", callback_data="main_menu")
                )
                builder.adjust(1)
                
                await callback.message.edit_text(
                    f"❌ Запись #{appointment_id} отменена:\n\n"
                    f"• Мастер: {deleted_appointment['master_name']}\n"
                    f"• Дата: {deleted_appointment['date']}\n"
                    f"• Время: {deleted_appointment['time']}\n"
                    f"• Услуга: {deleted_appointment['service_name']}\n\n"
                    f"Если была внесена предоплата, она будет возвращена в течение 24 часов.",
                    reply_markup=builder.as_markup()
                )
                return
    
    # Если запись не найдена
    await callback.answer("❌ Запись не найдена")

@router.callback_query(F.data == "about_studio")
async def about_studio(callback: CallbackQuery):
    """Информация о студии"""
    
    await callback.answer()
    
    text = """
🏠 Студия красоты "Эстетика"

📍 Адрес: ул. Красивая, д. 123
🕒 Часы работы: 9:00 - 21:00
📞 Телефон: +7 (XXX) XXX-XX-XX

✨ Наши преимущества:
• Опытные мастера с сертификатами
• Качественные материалы
• Уютная атмосфера
• Индивидуальный подход

Мы находимся в самом центре города, 
рядом с метро "Центральная".
    """
    
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="📅 Записаться", callback_data="book_appointment"),
        InlineKeyboardButton(text="🏠 В главное меню", callback_data="main_menu")
    )
    builder.adjust(1)
    
    await callback.message.edit_text(
        text,
        reply_markup=builder.as_markup()
    )

@router.callback_query(F.data == "contacts")
async def show_contacts(callback: CallbackQuery):
    """Показать контакты"""
    
    await callback.answer()
    
    text = """
📞 Контакты:

Телефон: +7 (XXX) XXX-XX-XX
Email: info@beauty-studio.ru
Адрес: ул. Красивая, д. 123

📱 Социальные сети:
Instagram: @beauty_studio
VK: vk.com/beauty_studio

🕒 Режим работы:
Пн-Пт: 9:00 - 21:00
Сб-Вс: 10:00 - 20:00

📍 Как добраться:
Метро "Центральная", 5 минут пешком
    """
    
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="📅 Записаться", callback_data="book_appointment"),
        InlineKeyboardButton(text="🏠 В главное меню", callback_data="main_menu")
    )
    builder.adjust(1)
    
    await callback.message.edit_text(
        text,
        reply_markup=builder.as_markup()
    )

@router.callback_query(F.data == "cancel")
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    """Отмена действия"""
    
    await callback.answer("Действие отменено")
    await state.clear()
    
    await go_to_main_menu(callback)

def get_master_name(master_id):
    """Получить имя мастера по ID"""
    masters = {
        "1": "Анна",
        "2": "Мария", 
        "3": "Елена"
    }
    return masters.get(str(master_id), "Неизвестный мастер")