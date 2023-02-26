import utils
import re

from filters import DeleteOneKey, CallbackQueryFilter

from handlers.user.makups import Markups

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

from data.config import API_KEY

from language_packages import LanguagePackage

from loader import dp, bot

from patterns import format_pattern

from states.user import *

from typing import Dict

language_package = LanguagePackage().decorator
markups = Markups()

all_state = '*'
default_language = 'ru'
show_locations_button_numeric = {'1', '2', '3', '4', '5'}
delete_one_buttons = {f'delete_one {i}' for i in range(1, 6)}
location_live_period = 120
delete_one_key_pattern = re.compile(r'(delete_one [1-5])')


# @dp.message_handler(CommandHelp(), state=all_state)
# @language_package
# async def command_help(message: types.Message, state: FSMContext, language: Dict):
#     await state.finish()
#
#     await message.answer(message.get_full_command().__str__())


# ___________________________________ Start ___________________________________ #
@dp.message_handler(CommandStart(), state=all_state)
@language_package
async def start_bot(message: types.Message, state: FSMContext, language: Dict):
    await state.finish()

    error_status = language.get('start_error_status')
    success_status = language.get('start_success_status')
    reply_markup = await markups.main_menu(language)

    status = await utils.register_user(tg_id=message.from_user.id,
                                       first_name=message.from_user.first_name,
                                       second_name=message.from_user.last_name)

    if not status:
        await message.answer(error_status)
        return

    await message.answer(success_status, reply_markup=reply_markup)


# INFO
@dp.message_handler(Text(equals='Что это?'), state='*')
@language_package
async def what_is_it(message: types.Message, state: FSMContext, language: Dict):
    text = """asd
asd
asd
"""

    await message.reply(text)


@dp.message_handler(Text(equals='Как пользоваться ботом?'), state='*')
@language_package
async def how_to_use_it(message: types.Message, state: FSMContext, language: Dict):
    text = """asd
asd
asd
"""

    await message.reply(text)


@dp.message_handler(Text(equals='Команды'), state=all_state)
@language_package
async def send_commands(message: types.Message, state: FSMContext, language: Dict):
    text = 'Info'
    reply_markup = await markups.commands(language)

    await message.reply(text, reply_markup=reply_markup)


# ___________________________________ Addition Location ___________________________________ #
@dp.callback_query_handler(CallbackQueryFilter('add_location'))
@language_package
async def add_location(callback_query: types.CallbackQuery, state: FSMContext, language: Dict):
    await bot.answer_callback_query(callback_query.id)

    user_id = callback_query.from_user.id
    add_location_text = language.get('add_location_text')
    reply_markup = await markups.location_menu(language)

    await bot.send_message(chat_id=user_id,
                           text=add_location_text,
                           reply_markup=reply_markup)


# ___________________________________ Show Location ___________________________________ #
@dp.callback_query_handler(CallbackQueryFilter('show_locations'))
@language_package
async def show_locations(callback_query: types.CallbackQuery, state: FSMContext, language: Dict):
    await state.finish()
    await bot.answer_callback_query(callback_query.id)

    user_id = callback_query.from_user.id
    message_id = callback_query.message.message_id

    data = await utils.get_locations(user_id)

    if not data:
        doesnt_have_data = language.get('doesnt_have_data')
        reply_markup = await markups.commands(language, show=False, reset=False)

        await bot.edit_message_text(text=doesnt_have_data,
                                    chat_id=user_id,
                                    message_id=message_id,
                                    reply_markup=reply_markup)
        return

    keyboard = await markups.show_locations_list_keyboard(data)
    show_locations_list = language.get('show_locations_list')

    await bot.edit_message_text(
        text=show_locations_list,
        chat_id=user_id,
        message_id=message_id,
        reply_markup=keyboard
    )


@dp.callback_query_handler(CallbackQueryFilter(show_locations_button_numeric))
@language_package
async def show_locations_button_activate(callback_query: types.CallbackQuery, state: FSMContext, language: Dict):
    await state.finish()
    await bot.answer_callback_query(callback_query.id)

    user_id = callback_query.from_user.id
    message_id = callback_query.message.message_id

    data = await utils.get_locations(user_id)
    location: dict = data.get(callback_query.data)

    show_saved_locations_text = language.get('show_saved_locations_text')
    remove = language.get('remove')

    if not location:
        maybe_deleted = language.get('maybe_deleted')
        await bot.edit_message_text(maybe_deleted, user_id, message_id)
        return

    if location.get('img'):
        button_num = callback_query.data

        img_path = f"data/imgs/{user_id}_{button_num}.png"
        path = utils.get_project_path() + img_path
        io_ = open(path, mode='rb')

        await bot.send_photo(user_id, io_)

    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    keyboard.add(InlineKeyboardButton(remove, callback_data=f'delete_one {callback_query.data}'))

    text = await format_pattern(show_saved_locations_text, **location)

    await bot.send_message(user_id, text, reply_markup=keyboard, parse_mode=types.ParseMode.HTML)


@dp.callback_query_handler(DeleteOneKey(delete_one_key_pattern))
@language_package
async def delete_one(callback_query: types.CallbackQuery, state: FSMContext, language: Dict):
    await state.finish()
    await bot.answer_callback_query(callback_query.id)

    user_id = callback_query.from_user.id
    location = await utils.get_locations(user_id)
    message_id = callback_query.message.message_id

    if not location:
        doesnt_have_data = language.get('doesnt_have_data')
        reply_markup = await markups.commands(language, show=False, reset=False)

        await bot.edit_message_text(doesnt_have_data, user_id, message_id, reply_markup=reply_markup)
        return

    button_prefix = callback_query.data.split()[-1]
    deleted = await utils.delete_one(user_id, location, button_prefix)

    if not deleted:
        maybe_deleted = language.get('maybe_deleted')

        await bot.send_message(user_id, maybe_deleted)
        return

    success_location_deleted = language.get('success_location_deleted')

    await bot.send_message(user_id, success_location_deleted)


@dp.callback_query_handler(CallbackQueryFilter('reset_list'))
@language_package
async def reset_list(callback_query: types.CallbackQuery, state: FSMContext, language: Dict):
    await state.finish()
    await bot.answer_callback_query(callback_query.id)

    user_id = callback_query.from_user.id

    are_you_sure = language.get('are_you_sure')
    yes = language.get('yes')
    no = language.get('no')

    keyboard = await markups.get_reply_keyboard_use_str(yes, no)

    await bot.send_message(user_id, are_you_sure, reply_markup=keyboard)

    await state.set_state(DeleteState.delete_state.state)


@dp.message_handler(content_types=types.ContentType.TEXT, state=DeleteState.delete_state)
@language_package
async def delete_state(message: types.Message, state: FSMContext, language: Dict):
    message_text = message.text
    user_id = message.from_user.id

    yes = language.get('yes')
    no = language.get('no')
    reply_markup = await markups.main_menu(language)

    if message_text == yes:

        deleted = await utils.delete_data(user_id)

        if deleted:
            success_all_location_deleted = language.get('success_all_location_deleted')
            await message.answer(success_all_location_deleted, reply_markup=reply_markup)

        else:
            doesnt_have_data = language.get('doesnt_have_data')
            await message.answer(doesnt_have_data, reply_markup=reply_markup)

    elif message_text == no:
        cancel = language.get('canceling')
        await message.answer(cancel, reply_markup=reply_markup)

    await state.finish()


# Auto Locate
@dp.message_handler(Text(equals='Определить по геолокации'))
@language_package
async def auto_location(message: types.Message, state: FSMContext, language: Dict):

    send_location = language.get('send_location')
    cancel = language.get('cancel')
    send_your_location = language.get('send_your_location')

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton(send_location, request_location=True))
    keyboard.add(KeyboardButton(cancel))

    await message.answer(send_your_location, reply_markup=keyboard)
    await state.set_state(AutoAdditionLocation.location.state)


@dp.message_handler(content_types=types.ContentType.TEXT, state=AutoAdditionLocation.location)
@language_package
async def another(message: types.Message, state: FSMContext, language: Dict):
    await state.finish()
    await all_requests(message, state)


@dp.message_handler(content_types=types.ContentType.LOCATION, state=AutoAdditionLocation.location)
@language_package
async def auto_location(message: types.Message, state: FSMContext, language: Dict):
    lat = message.location.latitude
    lon = message.location.longitude

    await state.update_data(location=(lon, lat))
    await state.set_state(AutoAdditionLocation.name.state)

    query_text = language.get('query_text')

    await message.answer(query_text)


@dp.message_handler(content_types=types.ContentType.TEXT, state=AutoAdditionLocation.name)
@language_package
async def setting_name_location(message: types.Message, state: FSMContext, language: Dict):
    if message.text.__len__() > 50:
        query_len_error = language.get('query_len_error')

        await message.answer(query_len_error)
        return

    await state.update_data(name=message.text)

    data = await state.get_data()
    location = data.get('location')
    lat = location[1]
    lon = location[0]
    places = await utils.get_place(name=message.text, longitude=lon, latitude=lat, radius=1000, api_key=API_KEY)

    if not places:
        reply_markup = await markups.main_menu(language)
        query_not_found = language.get('query_not_found')

        await message.answer(query_not_found, reply_markup=reply_markup)
        await state.finish()

        return

    components = await utils.get_many_components(places)
    components = await utils.add_distance(components, location)
    components = utils.get_five_elements(components)

    pattern_text = language.get('show_saved_locations_text')

    cur_component = utils.get_cur_component(components, 0)
    distance = cur_component.get('distance')

    text, component_lat, component_lon = await utils.get_component_materials(cur_component, pattern_text)
    text += "\n" + language.get('default_position')
    text += "\n\n" + language.get('distance').format(distance)

    location_img = await bot.send_location(message.from_user.id,
                                           latitude=component_lat,
                                           longitude=component_lon,
                                           live_period=location_live_period,
                                           proximity_alert_radius=10000)  # ???

    reply_markup = await markups.show_location(language)
    msg = await message.answer(text, reply_markup=reply_markup)

    location_img_id = location_img.message_id
    msg_id = msg.message_id

    await state.update_data(components=components, location_img_id=location_img_id,
                            msg_id=msg_id, cur_component_num=0, location_img=location_img)

    await state.set_state(AutoAdditionLocation.name.state)


@dp.callback_query_handler(CallbackQueryFilter({'back', 'next'}), state=AutoAdditionLocation.name)
@language_package
async def display_locations(callback_query: types.CallbackQuery, state: FSMContext, language: Dict):
    await bot.answer_callback_query(callback_query.id)

    data = await state.get_data()
    user_id = callback_query.from_user.id

    cur_component_num = data.get('cur_component_num')

    if callback_query.data == 'back':
        if cur_component_num < 1:
            return
        cur_component_num -= 1

    else:
        if cur_component_num > 3:
            return
        cur_component_num += 1

    components = data.get('components')
    location_img_id = data.get('location_img_id')
    msg_id = data.get('msg_id')

    pattern_text = language.get('show_saved_locations_text')

    cur_component = utils.get_cur_component(components, cur_component_num)
    distance = cur_component.get('distance')

    text, component_lat, component_lon = await utils.get_component_materials(cur_component, pattern_text)
    text += f"\nПозиция: {cur_component_num + 1} из 5"
    text += f"\n\nРастояние от вас: {distance} м."

    location_img = await bot.edit_message_live_location(latitude=component_lat,
                                                        longitude=component_lon,
                                                        chat_id=user_id,
                                                        message_id=location_img_id)

    reply_markup = await markups.show_location(language)
    msg = await bot.edit_message_text(text, user_id, msg_id, reply_markup=reply_markup)

    msg_id = msg.message_id

    await state.update_data(msg_id=msg_id, cur_component_num=cur_component_num, location_img=location_img)


@dp.callback_query_handler(CallbackQueryFilter('choose'), state=AutoAdditionLocation.name)
@language_package
async def display_locations(callback_query: types.CallbackQuery, state: FSMContext, language: Dict):
    await bot.answer_callback_query(callback_query.id)

    data = await state.get_data()
    user_id = callback_query.from_user.id

    cur_component_num = data.get('cur_component_num')
    components = data.get('components')

    cur_component = utils.get_cur_component(components, cur_component_num)
    reply_markup = await markups.main_menu(language)

    result = await utils.add_data(
        tg_id=user_id,
        **cur_component
    )

    if not result:
        await bot.send_message(user_id, 'Что-то пошло не так. Попробуйте еще', reply_markup=reply_markup)
        await state.finish()

    else:
        await bot.send_message(user_id, 'Сохранено!', reply_markup=reply_markup)

    location_img_id = data.get('location_img_id')
    msg_id = data.get('msg_id')

    await bot.delete_message(user_id, location_img_id)
    await bot.delete_message(user_id, msg_id)

    await state.finish()


# @dp.callback_query_handler(lambda c: c.data == 'show_all', state=AutoAdditionLocation.name)
# async def display_locations(callback_query: types.CallbackQuery, state: FSMContext):
#     await bot.answer_callback_query(callback_query.id)
#
#     data = await state.get_data()
#     user_id = callback_query.from_user.id
#     language = language_package.get_language_package(callback_query.from_user.language_code)
#
#     components = data.get('components')
#
#     ...


# ___________________________________ HandSetting Location ___________________________________ #
@dp.message_handler(Text(equals='Добавить новое'))
@language_package
async def add_new_location(message: types.Message, state: FSMContext, language: Dict):
    await state.finish()

    location_list_len = await utils.location_list_len(message.from_user.id)
    reply_markup = await markups.main_menu(language)

    if location_list_len > 4:
        await message.answer(
            'У вас слишком много сохраненных мест! Удалите лишьнее, чтобы дальше сохранять места!',
            reply_markup=reply_markup)
        return

    await message.answer('Введите название вашего места',
                         reply_markup=ReplyKeyboardMarkup(resize_keyboard=True)
                         .add(KeyboardButton('Отменить')))

    await state.set_state(HandAdditionLocation.name.state)


@dp.message_handler(content_types=types.ContentType.TEXT, state=HandAdditionLocation.name)
@language_package
async def hand_setting_name(message: types.Message, state: FSMContext, language: Dict):

    reply_markup = await markups.main_menu(language)

    if message.text == 'Отменить':
        await state.finish()
        await message.answer('Действие отменено', reply_markup=reply_markup)
        return

    await state.update_data(name=message.text)

    await message.answer('Включите местоположение',
                         reply_markup=ReplyKeyboardMarkup(resize_keyboard=True)
                         .add(KeyboardButton('Определить местоположение', request_location=True))
                         .add(KeyboardButton('Отменить')))

    await state.set_state(HandAdditionLocation.location.state)


@dp.message_handler(content_types=types.ContentType.LOCATION, state=HandAdditionLocation.location)
@language_package
async def hand_setting_location(message: types.Message, state: FSMContext, language: Dict):
    await message.answer('Определяю местоположение...')

    lat = message.location.latitude
    lon = message.location.longitude

    await state.update_data(location=(lat, lon))

    await message.answer('Будет изображение этого места?', reply_markup=ReplyKeyboardMarkup(resize_keyboard=True)
                         .add(KeyboardButton('Да'))
                         .add(KeyboardButton('Нет')))

    await state.set_state(HandAdditionLocation.img.state)


@dp.message_handler(state=HandAdditionLocation.img)
@language_package
async def hand_setting_img(message: types.Message, state: FSMContext, language: Dict):
    if (mes := message.text.lower()) == 'да':
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(KeyboardButton('Отменить'))
        await message.answer('Отправьте мне фото вашего места', reply_markup=keyboard)
        await state.set_state(HandAdditionLocation.img_.state)

    elif mes == 'нет':
        await message.answer('Будет информация для этого места?',
                             reply_markup=ReplyKeyboardMarkup(resize_keyboard=True)
                             .add(KeyboardButton('Да'))
                             .add(KeyboardButton('Нет')))
        await state.set_state(HandAdditionLocation.info.state)

    else:
        await message.reply('Некоректный ввод, выберите пожалуйста с клавиатуры.')


@dp.message_handler(content_types=types.ContentType.PHOTO, state=HandAdditionLocation.img_)
@language_package
async def hand_setting_img_(message: types.Message, state: FSMContext, language: Dict):
    await state.update_data(img=True)
    await message.answer('Сохранение...')

    location_list_len = await utils.location_list_len(message.from_user.id)
    imgs_path = f'data/imgs/{message.from_user.id}_{location_list_len + 1}.png'

    path = utils.get_project_path() + imgs_path

    await message.photo[-1].download(destination_file=path)

    await message.answer('Будет информация для этого места?', reply_markup=ReplyKeyboardMarkup(resize_keyboard=True)
                         .add(KeyboardButton('Да'))
                         .add(KeyboardButton('Нет')))
    await state.set_state(HandAdditionLocation.info.state)


@dp.message_handler(state=HandAdditionLocation.info)
@language_package
async def hand_setting_info(message: types.Message, state: FSMContext, language: Dict):
    if (mes := message.text.lower()) == 'да':
        await message.answer('Отправьте мне текст')
        await state.set_state(HandAdditionLocation.info_.state)

    elif mes == 'нет':
        await _saving_data(message, state)

    else:
        await message.reply('Некоректный ввод, выберите пожалуйста с клавиатуры.')


@dp.message_handler(content_types=types.ContentType.TEXT, state=HandAdditionLocation.info_)
@language_package
async def _saving_data(message: types.Message, state: FSMContext, language: Dict):
    await state.update_data(info=message.text)

    await message.answer('Сохранение...')
    await state.set_state(HandAdditionLocation.cancel.state)

    data = await state.get_data()
    result = await utils.add_data(tg_id=message.from_user.id,
                                  latitude=data.get('location')[0],
                                  longitude=data.get('location')[1],
                                  name=data.get('name'),
                                  img=data.get('img'),
                                  info=data.get('info'))

    reply_markup = await markups.main_menu(language)

    if not result:
        await message.answer('Что-то пошло не так. Попробуйте еще', reply_markup=reply_markup)

    else:
        await message.answer('Сохранено!', reply_markup=reply_markup)

    await state.finish()


@dp.message_handler(Text(equals='Отменить'), state=HandAdditionLocation)
@language_package
async def closing(message: types.Message, state: FSMContext, language: Dict):
    await state.finish()

    reply_markup = await markups.main_menu(language)
    answer = language.get('action_canceled')

    await message.answer(answer, reply_markup=reply_markup)


@dp.message_handler(state=HandAdditionLocation)
@language_package
async def another_text(message: types.Message, state: FSMContext, language: Dict):

    input_correct = language.get('input_correct')

    await message.answer(input_correct)


@dp.message_handler(state=all_state)
@language_package
async def all_requests(message: types.Message, state: FSMContext, language: Dict):
    reply_markup = await markups.main_menu(language)

    cancel = language.get('cancel')

    if message.text == cancel:
        canceling = language.get("canceling")

        await message.reply(canceling, reply_markup=reply_markup)
        await state.finish()

    else:
        await message.answer('MainMenu', reply_markup=reply_markup)
