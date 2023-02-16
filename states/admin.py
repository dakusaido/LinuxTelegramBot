from aiogram.dispatcher.filters.state import StatesGroup, State

__all__ = ['Mail']


class Mail(StatesGroup):
    mail = State()
