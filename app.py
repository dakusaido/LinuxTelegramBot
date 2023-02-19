import logging

from aiogram import executor

from utils import create_base
from handlers import dp, bot
from filters import setup


async def on_startup(dp):
    create_base()
    setup(dp)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, on_startup=on_startup)
