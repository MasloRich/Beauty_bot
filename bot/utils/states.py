from aiogram.fsm.state import State, StatesGroup

class ClientStates(StatesGroup):
    """Состояния клиента"""
    choosing_master = State()
    choosing_service = State()
    choosing_date = State()
    choosing_time = State()
    confirming_booking = State()

class MasterStates(StatesGroup):
    """Состояния мастера"""
    editing_schedule = State()
    adding_service = State()

class AdminStates(StatesGroup):
    """Состояния администратора"""
    adding_master = State()
    viewing_stats = State()