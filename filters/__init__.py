from aiogram import Dispatcher
from .filters import PrivateChatFilter


def setup(dp: Dispatcher):
    dp.filters_factory.bind(PrivateChatFilter)