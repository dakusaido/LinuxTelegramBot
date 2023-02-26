from aiogram import Dispatcher
from .filters import PrivateChatFilter, DeleteOneKey, CallbackQueryFilter

__all__ = ['PrivateChatFilter', 'DeleteOneKey', 'CallbackQueryFilter']


def setup(dp: Dispatcher):
    for filter_ in [PrivateChatFilter, DeleteOneKey, CallbackQueryFilter]:
        dp.filters_factory.bind(filter_)
