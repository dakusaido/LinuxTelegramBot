from aiogram.dispatcher.filters.state import StatesGroup, State

__all__ = ['HandAdditionLocation', 'DeleteState', 'AutoAdditionLocation']


class HandAdditionLocation(StatesGroup):
    name = State()
    location = State()
    img = State()
    img_ = State()
    info = State()
    info_ = State()
    cancel = State()


class AutoAdditionLocation(StatesGroup):
    location = State()
    name = State()
    components = State()
    names = State()


class DeleteState(StatesGroup):
    delete_state = State()
