import handlers.admin.makups.makups as nav

from asyncio import sleep

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from data.config.config import ADMINS_ID
from loader import dp, bot
from states.admin import Mail
from utils.sql_commands import select_users


@dp.message_handler(Text(equals='mail'), user_id=ADMINS_ID, state='*')
async def mail(message: types.Message):
    await message.answer(
        '<b>💌 Отправьте сообщение для рассылки:</b>'
    )
    await Mail.mail.set()


@dp.message_handler(state=Mail.mail, content_types=types.ContentType.ANY)
async def mail_on(message: types.Message, state: FSMContext):
    await state.reset_state(with_data=False)
    if types.ContentType.TEXT == message.content_type:  # Если админ отправил текст
        for user in select_users():
            try:
                await dp.bot.send_message(
                    chat_id=user.tg_id,
                    text=message.html_text
                )
                await sleep(0.33)
            except Exception as e:
                print(e)
                pass
        else:
            await message.answer(
                '<b>✅ Рассылка завершена!</b>', reply_markup=nav.mainMenu
            )

    elif types.ContentType.PHOTO == message.content_type:  # Если админ отправил фото
        for user in select_users():
            try:
                await dp.bot.send_photo(
                    chat_id=user.tg_id,
                    photo=message.photo[-1].file_id,
                    caption=message.html_text if message.caption else None
                )
                await sleep(0.33)
            except Exception:
                pass
        else:
            await message.answer(
                '<b>✅ Рассылка завершена!</b>', reply_markup=nav.mainMenu
            )

    elif types.ContentType.VIDEO == message.content_type:  # Если админ отправил видео
        for user in select_users():
            try:
                await dp.bot.send_video(
                    chat_id=user.tg_id,
                    video=message.video.file_id,
                    caption=message.html_text if message.caption else None
                )
                await sleep(0.33)
            except Exception:
                pass
        else:
            await message.answer(
                '<b>✅ Рассылка завершена!</b>', reply_markup=nav.mainMenu
            )

    elif types.ContentType.ANIMATION == message.content_type:  # Если админ отправил gif
        for user in select_users():
            try:
                await dp.bot.send_animation(
                    chat_id=user.tg_id,
                    animation=message.animation.file_id,
                    caption=message.html_text if message.caption else None
                )
                await sleep(0.33)
            except Exception:
                pass
        else:
            await message.answer(
                '<b>✅ Рассылка завершена!</b>', reply_markup=nav.mainMenu
            )
    elif types.ContentType.STICKER == message.content_type:  # Если админ отправил sticker
        for user in select_users():
            try:
                await dp.bot.send_sticker(
                    chat_id=user.tg_id,
                    sticker=message.sticker.file_id,
                )
                await sleep(0.33)
            except Exception:
                pass
        else:
            await message.answer(
                '<b>✅ Рассылка завершена!</b>', reply_markup=nav.mainMenu
            )

    else:
        await message.answer(
            '<b>❗️ Данный формат контента не поддерживается для рассылки!</b>', reply_markup=nav.mainMenu
        )
