from aiogram.dispatcher.filters.state import StatesGroup, State


class Mail(StatesGroup):
    mail = State()
