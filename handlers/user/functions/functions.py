import utils

from handlers.user.makups import Markups as nav

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart, Command
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

from data.config import ADMINS_ID, API_KEY

from language_packages import LanguagePackage

from loader import dp, bot

from patterns import format_pattern

from states.user import *

__all__ = ['dp', 'bot']

language_package = LanguagePackage()

all_state = '*'
default_language = 'ru'
show_locations_button_numeric = {'1', '2', '3', '4', '5'}
delete_one_buttons = {f'delete_one {i}' for i in range(1, 6)}


# ___________________________________ Start ___________________________________ #
@dp.message_handler(CommandStart(), state='*')
async def start_bot(message: types.Message, state: FSMContext):
    await state.finish()

    language = language_package.get_language_package(message.from_user.language_code)

    error_status = language.get('start_error_status')
    success_status = language.get('start_success_status')

    status = utils.register_user(tg_id=message.from_user.id,
                                 first_name=message.from_user.first_name,
                                 second_name=message.from_user.last_name)

    if not status:
        await message.answer(error_status)
        return

    await message.answer(success_status, reply_markup=nav.mainMenu(language))


# ___________________________________ Show Profile ___________________________________ #
@dp.message_handler(Command(['showProfile']), state='*')  # Not realized
async def show_profile(message: types.Message, state: FSMContext):
    user = utils.get_user(message.from_user.id)

    await message.reply(f"{user.first_name} {user.second_name}")


# ___________________________________ Addition Location ___________________________________ #
@dp.callback_query_handler(lambda c: c.data == 'add_location')
async def add_location(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)

    language = language_package.get_language_package(callback_query.from_user.language_code)

    add_location_text = language.get('add_location_text')

    await bot.send_message(chat_id=callback_query.from_user.id,
                           text=add_location_text,
                           reply_markup=nav.locationMenu(language))


# ___________________________________ Show Location ___________________________________ #
@dp.callback_query_handler(lambda c: c.data == 'show_locations')
async def show_locations(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await bot.answer_callback_query(callback_query.id)

    user_id = callback_query.from_user.id
    data = utils.get_locations(user_id)

    language = language_package.get_language_package(callback_query.from_user.language_code)
    doesnt_have_data = language.get('doesnt_have_data')

    if not data:
        await bot.send_message(user_id, doesnt_have_data)
        return

    keyboard = InlineKeyboardMarkup(resize_keyboard=True)

    for key, value in data.items():
        keyboard.add(InlineKeyboardButton(f"#{key} {value.get('name')}", callback_data=key))

    show_locations_list = language.get('show_locations_list')

    await bot.send_message(user_id, show_locations_list, reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data in show_locations_button_numeric)
async def show_locations_button_activate(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await bot.answer_callback_query(callback_query.id)

    user_id = callback_query.from_user.id

    data = utils.get_locations(user_id)
    location: dict = data.get(callback_query.data)

    language = language_package.get_language_package(callback_query.from_user.language_code)
    show_saved_locations_text = language.get('show_saved_locations_text')

    text = format_pattern(show_saved_locations_text, **location)
    remove = language.get('remove')

    if location.get('img'):
        button_num = callback_query.data

        img_path = f"data/imgs/{user_id}_{button_num}.png"
        path = utils.get_project_path() + img_path

        await bot.send_photo(user_id, open(path, mode='rb'))

    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    keyboard.add(InlineKeyboardButton(remove, callback_data=f'delete_one {callback_query.data}'))

    await bot.send_message(user_id, text, reply_markup=keyboard, parse_mode=types.ParseMode.HTML)


@dp.callback_query_handler(lambda c: c.data in delete_one_buttons)
async def delete_one(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await bot.answer_callback_query(callback_query.id)

    language = language_package.get_language_package(callback_query.from_user.language_code)
    doesnt_have_data = language.get('doesnt_have_data')
    maybe_deleted = language.get('maybe_delete')
    success_location_deleted = language.get('success_location_deleted')

    user_id = callback_query.from_user.id
    location = utils.get_locations(user_id)

    if not location:
        await bot.send_message(user_id, doesnt_have_data)
        return

    button_prefix = callback_query.data.split()[-1]
    deleted = utils.delete_one(user_id, location, button_prefix)

    if not deleted:
        await bot.send_message(user_id, maybe_deleted)
        return

    await bot.send_message(user_id, success_location_deleted)


@dp.callback_query_handler(lambda c: c.data == 'reset_list')
async def reset_list(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await bot.answer_callback_query(callback_query.id)

    user_id = callback_query.from_user.id

    language = language_package.get_language_package(callback_query.from_user.language_code)
    are_you_sure = language.get('are_you_sure')
    yes = language.get('yes')
    no = language.get('no')

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(yes)
    keyboard.add(no)

    await bot.send_message(user_id, are_you_sure, reply_markup=keyboard)

    await state.set_state(DeleteState.delete_state.state)


@dp.message_handler(content_types=types.ContentType.TEXT, state=DeleteState.delete_state)
async def delete_state(message: types.Message, state: FSMContext):
    message_text = message.text
    user_id = message.from_user.id

    language = language_package.get_language_package(message.from_user.language_code)
    yes = language.get('yes')
    no = language.get('no')
    success_all_location_deleted = language.get('success_all_location_deleted')
    doesnt_have_data = language.get('doesnt_have_data')
    cancel = language.get('canceling')

    if message_text == yes:

        deleted = utils.delete_data(user_id)

        if deleted:
            await message.answer(success_all_location_deleted, reply_markup=nav.mainMenu(language))

        else:
            await message.answer(doesnt_have_data, reply_markup=nav.mainMenu(language))

    elif message_text == no:
        await message.answer(cancel, reply_markup=nav.mainMenu(language))

    await state.finish()


# Auto Locate
@dp.message_handler(Text(equals='Определить по геолокации'))
async def auto_location(message: types.Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('Отправить геолокацию', request_location=True))
    keyboard.add(KeyboardButton('Отменить'))

    await message.answer('Отправьте ваше местоположение', reply_markup=keyboard)
    await state.set_state(AutoAdditionLocation.location.state)


@dp.message_handler(content_types=types.ContentType.TEXT, state=AutoAdditionLocation.location)
async def another(message: types.Message, state: FSMContext):
    await state.finish()
    await all_requests(message, state)


@dp.message_handler(content_types=types.ContentType.LOCATION, state=AutoAdditionLocation.location)
async def handle_location(message: types.Message, state: FSMContext):
    lat = message.location.latitude
    lon = message.location.longitude

    await state.update_data(location=(lon, lat))
    await state.set_state(AutoAdditionLocation.name.state)

    await message.answer(
        'Что вас интересует. Имейте ввиду, чем точнее будет название, тем лучше будет результат.\n\n' +
        'К примеру - Добрая столовая')


@dp.message_handler(content_types=types.ContentType.TEXT, state=AutoAdditionLocation.name)
async def setting_name_location(message: types.Message, state: FSMContext):
    language = language_package.get_language_package(message.from_user.language_code)

    if message.text.__len__() > 50:
        await message.answer('Извините, однако запрос слишком большой. Поробуйте сократить запрос.')
        return

    await state.update_data(name=message.text)

    data = await state.get_data()
    location = data.get('location')
    lat = location[1]
    lon = location[0]
    places = utils.get_place(name=message.text, longitude=lon, latitude=lat, radius=1000, api_key=API_KEY)

    if not places:
        await message.answer('По вашему запросу нечего не было найдено.',
                             reply_markup=nav.mainMenu(language))
        await state.finish()
        return

    components = utils.get_many_components(places)
    components = utils.add_distance(components, location)
    components = utils.get_five_elements(components)

    pattern_text = language.get('show_saved_locations_text')

    cur_component = utils.get_cur_component(components, 0)
    cur_component.update(cur_component_num=1)
    text, component_lat, component_lon = utils.get_component_materials(cur_component, pattern_text)

    location_img = await bot.send_location(message.from_user.id, latitude=component_lat, longitude=component_lon)
    msg = await message.answer(text, reply_markup=nav.showLocation(language))

    location_img_id = location_img.message_id
    msg_id = msg.message_id

    await state.update_data(components=components, cur_component_num=0,
                            location_img_id=location_img_id, msg_id=msg_id)

    await state.set_state(AutoAdditionLocation.name.state)


@dp.callback_query_handler(lambda c: c.data in {'back', 'next'}, state=AutoAdditionLocation.name)
async def display_locations(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)

    data = await state.get_data()
    user_id = callback_query.from_user.id
    language = language_package.get_language_package(callback_query.from_user.language_code)

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
    cur_component.update(cur_component_num=cur_component_num + 1)
    text, component_lat, component_lon = utils.get_component_materials(cur_component, pattern_text)

    # await bot.edit_message_live_location(latitude=component_lat,
    #                                      longitude=component_lon,
    #                                      chat_id=user_id,
    #                                      message_id=location_img_id)
    #

    msg = await bot.edit_message_text(text, user_id, msg_id, reply_markup=nav.showLocation(language))

    msg_id = msg.message_id

    await state.update_data(msg_id=msg_id, cur_component_num=cur_component_num)

# ___________________________________ HandSetting Location ___________________________________ #
@dp.message_handler(Text(equals='Добавить новое'))
async def add_new_location(message: types.Message, state: FSMContext):
    await state.finish()

    language = language_package.get_language_package(message.from_user.language_code)

    if utils.location_list_len(message.from_user.id) > 4:
        await message.answer(
            'У вас слишком много сохраненных мест! Удалите лишьнее, чтобы дальше сохранять места!',
            reply_markup=nav.mainMenu(language))
        return

    await message.answer('Введите название вашего места',
                         reply_markup=ReplyKeyboardMarkup(resize_keyboard=True)
                         .add(KeyboardButton('Отменить')))

    await state.set_state(HandAdditionLocation.name.state)


@dp.message_handler(content_types=types.ContentType.TEXT, state=HandAdditionLocation.name)
async def hand_setting_name(message: types.Message, state: FSMContext):
    language = language_package.get_language_package(message.from_user.language_code)

    if message.text == 'Отменить':
        await state.finish()
        await message.answer('Действие отменено', reply_markup=nav.mainMenu(language))
        return

    await state.update_data(name=message.text)

    await message.answer('Включите местоположение',
                         reply_markup=ReplyKeyboardMarkup(resize_keyboard=True)
                         .add(KeyboardButton('Определить местоположение', request_location=True))
                         .add(KeyboardButton('Отменить')))

    await state.set_state(HandAdditionLocation.location.state)


@dp.message_handler(content_types=types.ContentType.LOCATION, state=HandAdditionLocation.location)
async def hand_setting_location(message: types.Message, state: FSMContext):
    await message.answer('Определяю местоположение...')

    lat = message.location.latitude
    lon = message.location.longitude

    await state.update_data(location=(lat, lon))

    await message.answer('Будет изображение этого места?', reply_markup=ReplyKeyboardMarkup(resize_keyboard=True)
                         .add(KeyboardButton('Да'))
                         .add(KeyboardButton('Нет')))

    await state.set_state(HandAdditionLocation.img.state)


@dp.message_handler(state=HandAdditionLocation.img)
async def hand_setting_img(message: types.Message, state: FSMContext):
    if (mes := message.text.lower()) == 'да':
        keybord = ReplyKeyboardMarkup(resize_keyboard=True)
        keybord.add(KeyboardButton('Отменить'))
        await message.answer('Отправьте мне фото вашего места', reply_markup=keybord)
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
async def hand_setting_img_(message: types.Message, state: FSMContext):
    await state.update_data(img=True)
    await message.answer('Сохранение...')

    imgs_path = f'data/imgs/{message.from_user.id}_{utils.location_list_len(message.from_user.id) + 1}.png'

    path = utils.get_project_path() + imgs_path

    await message.photo[-1].download(destination_file=path)

    await message.answer('Будет информация для этого места?', reply_markup=ReplyKeyboardMarkup(resize_keyboard=True)
                         .add(KeyboardButton('Да'))
                         .add(KeyboardButton('Нет')))
    await state.set_state(HandAdditionLocation.info.state)


@dp.message_handler(state=HandAdditionLocation.info)
async def hand_setting_info(message: types.Message, state: FSMContext):
    if (mes := message.text.lower()) == 'да':
        await message.answer('Отправьте мне текст')
        await state.set_state(HandAdditionLocation.info_.state)

    elif mes == 'нет':
        await _saving_data(message, state)

    else:
        await message.reply('Некоректный ввод, выберите пожалуйста с клавиатуры.')


@dp.message_handler(content_types=types.ContentType.TEXT, state=HandAdditionLocation.info_)
async def _saving_data(message: types.Message, state: FSMContext):
    await state.update_data(info=message.text)

    language = language_package.get_language_package(message.from_user.language_code)

    await message.answer('Сохранение...')
    await state.set_state(HandAdditionLocation.cancel.state)

    data = await state.get_data()
    result = utils.add_data(tg_id=message.from_user.id,
                            latitude=data.get('location')[0],
                            longitude=data.get('location')[1],
                            name=data.get('name'),
                            img=data.get('img'),
                            info=data.get('info'))

    if not result:
        await message.answer('Что-то пошло не так. Попробуйте еще', reply_markup=nav.mainMenu(language))

    else:
        await message.answer('Сохранено!', reply_markup=nav.mainMenu(language))

    await state.finish()


@dp.message_handler(Text(equals='Отменить'), state=HandAdditionLocation)
async def closing(message: types.Message, state: FSMContext):
    await state.finish()

    language = language_package.get_language_package(message.from_user.language_code)

    await message.answer('Действие отменено', reply_markup=nav.mainMenu(language))


@dp.message_handler(state=HandAdditionLocation)
async def another_text(message: types.Message, state: FSMContext):
    await message.answer("Вводите нормально!")


# INFO
@dp.message_handler(Text(equals='Что это?'), state='*')
async def what_is_it(message: types.Message, state: FSMContext):
    text = """asd
asd
asd
"""

    await message.reply(text)


@dp.message_handler(Text(equals='Как пользоваться ботом?'), state='*')
async def how_to_use_it(message: types.Message, state: FSMContext):
    text = """asd
asd
asd
"""

    await message.reply(text)


@dp.message_handler(Text(equals='Команды'), state='*')
async def send_commands(message: types.Message, state: FSMContext):
    language = language_package.get_language_package(message.from_user.language_code)

    text = 'Info'
    await message.reply(text, reply_markup=nav.commands(language))


@dp.message_handler(state='*')
async def all_requests(message: types.Message, state: FSMContext):
    language = language_package.get_language_package(message.from_user.language_code)

    if message.text == 'Отменить':
        await message.reply('Отмена..', reply_markup=nav.mainMenu(language))
        await state.finish()

    else:
        await message.answer('MainMenu', reply_markup=nav.mainMenu(language))
