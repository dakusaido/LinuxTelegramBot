import types

import utils
import handlers.user.makups.makups as nav

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

from data.config.config import ADMINS_ID, API_KEY

from loader import dp, bot

from handlers.admin import mainMenu as adminMainMenu

from patterns import show_saved_locations_text

from states.user import RegUser, HandAdditionLocation, DeleteState, AutoAdditionLocation


# Start
@dp.message_handler(CommandStart(), state='*')
async def start_bot(message: types.Message, state: FSMContext):
    if message.from_user.id in ADMINS_ID:
        await message.answer(
            'Привет, Владелец!', reply_markup=adminMainMenu
        )
        return

    await message.answer(
        'Привет!\nВведите свое имя и фамилию для регистрации'
    )

    await RegUser.reg_user.set()


# Registration
@dp.message_handler(state=RegUser.reg_user, content_types=types.ContentType.TEXT)
async def reg_user(message: types.Message, state: FSMContext):
    await state.reset_state(with_data=False)

    if (user := message.text.split(' ')).__len__() == 2:
        utils.register_user(tg_id=message.from_user.id, first_name=user[0], second_name=user[1])
        await message.answer("Регистрация прошла успешно!", reply_markup=nav.mainMenu)

    else:
        await message.answer("Упс... Что-то пошло не так, попробуйте еще.",
                             reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton('/start')]],
                                                              resize_keyboard=True))


# show profile
@dp.message_handler(commands=['showProfile'], state='*')
async def show_profile(message: types.Message, state: FSMContext):
    user = utils.get_user(message.from_user.id)

    await message.reply(' '.join(user))


@dp.callback_query_handler(lambda c: c.data == 'add_location')
async def add_location(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)

    await bot.send_message(callback_query.from_user.id,
                           'Чтобы добавить новую локацию, вы можете использовать геопозицию или добавить место вручную',
                           reply_markup=nav.locationMenu)


@dp.callback_query_handler(lambda c: c.data == 'show_locations')
async def show_locations(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)

    if not (data := utils.show_locations(callback_query.from_user.id)):
        await bot.send_message(callback_query.from_user.id, 'У вас пока что нет мест. Может попробует добавить?')
        return

    names = list(map(lambda key: (key, data.get(key).get('name')), data))
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)

    for (key, name) in names:
        keyboard.add(InlineKeyboardButton(f"#{key} {name}", callback_data=key))

    await bot.send_message(callback_query.from_user.id, "Вот список тех мест, которые вы сохраняли",
                           reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data in {'1', '2', '3', '4', '5'})
async def show_locations_button_activate(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await state.finish()

    if not (data := utils.show_locations(callback_query.from_user.id)):
        await bot.send_message(callback_query.from_user.id, 'У вас пока что нет мест. Может попробует добавить?')
        return

    location: dict = data.get(callback_query.data)

    default = 'Отсутствует'

    name = location.get('name') or default
    address = location.get('location') or default
    link = location.get('link') or default
    info = location.get('info') or default
    more_info = location.get('info') or default

    text = show_saved_locations_text.format(name, address, link, info, more_info)

    if location.get('img'):
        path = utils.get_project_path() + f"data/imgs/{callback_query.from_user.id}_{callback_query.data}.png"
        await bot.send_photo(callback_query.from_user.id, open(path, mode='rb'))

    else:
        text += "Изображение: Отсутствует"

    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    keyboard.add(InlineKeyboardButton('Удалить', callback_data=f'delete_one {callback_query.data}'))

    await bot.send_message(callback_query.from_user.id, text, reply_markup=keyboard, parse_mode=types.ParseMode.HTML)


@dp.callback_query_handler(lambda c: c.data in [f'delete_one {i}' for i in range(1, 6)])
async def delete_one(callback_query: types.CallbackQuery, state: FSMContext):
    if not (data := utils.show_locations(callback_query.from_user.id)):
        await bot.send_message(callback_query.from_user.id, 'У вас пока что нет мест. Может попробует добавить?')
        return

    if not utils.delete_one(callback_query.from_user.id, data, callback_query.data.split()[-1]):
        await bot.send_message(callback_query.from_user.id,
                               'Что-то пошло не так. Возможно вы уже удаляли раннее эту локацию')
        return

    await bot.send_message(callback_query.from_user.id,
                           'Ваша локация была успешно удалена!')


@dp.callback_query_handler(lambda c: c.data == 'reset_list')
async def reset_list(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await bot.answer_callback_query(callback_query.id)

    await bot.send_message(callback_query.from_user.id, "Вы уверены, что хотите все удалить?",
                           reply_markup=ReplyKeyboardMarkup(resize_keyboard=True)
                           .add('Да')
                           .add('Нет'))

    await state.set_state(DeleteState.delete_state.state)


@dp.message_handler(content_types=types.ContentType.TEXT, state=DeleteState.delete_state)
async def delete_state(message: types.Message, state: FSMContext):
    if message.text.lower() == 'да':
        if utils.delete_data(message.from_user.id):
            await message.answer("Все местоположения были успешно удалены!", reply_markup=nav.mainMenu)

        else:
            await message.answer("Упс... Что-то пошло не так, возможно вы ранее не создавали местоположения",
                                 reply_markup=nav.mainMenu)

    else:
        await message.answer('Отмена...', reply_markup=nav.mainMenu)

    await state.finish()


# Auto Locate
@dp.message_handler(Text(equals='Определить по геолокации'))
async def auto_location(message: types.Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('Отправить геолокацию', request_location=True))
    keyboard.add(KeyboardButton('Отменить'))

    await message.answer('Отправьте ваше местоположение', reply_markup=keyboard)
    await state.set_state(AutoAdditionLocation.location.state)


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
    if message.text.__len__() > 50:
        await message.answer('Извините, однако запрос слишком большой. Поробуйте сократить запрос.')
        return

    await state.update_data(name=message.text)

    data = await state.get_data()
    location = data.get('location')
    lon = location[0]
    lat = location[1]
    places = utils.get_place(name=message.text, longitude=lon, latitude=lat, radius=1000, api_key=API_KEY)
    print(places)

    if not places:
        await message.answer('По вашему запросу нечего не было найдено.')
        await state.finish()
        return

    components = list(map(lambda place: utils.get_components(place), places))
    print(components)
    names = list(map(lambda component: (component.get('name'), '300м'), components)) # ????????
    print(names)

    await state.update_data(components=components)
    await state.update_data(names=names)

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    for name in names:
        keyboard.add(KeyboardButton(' | '.join(name)))

    await message.answer('Выберите тот, который хотите записать', reply_markup=keyboard)

    await state.set_state(AutoAdditionLocation.components.state)


@dp.message_handler(content_types=types.ContentType.TEXT, state=AutoAdditionLocation.components)
async def getting_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    names = data.get('names')

    if message.text not in names:
        await message.answer('Такого места в списке нет.')
        return

    text = message.text.split(' | ')
    components = data.get('components')
    result = list(filter(lambda tup: (tup[0] == text[0]) and (tup[1] == text[1]), components))
    # location = data.get('location')
    # lon = location[0]
    # lat = location[1]
    #
    # utils.add_data(message.from_user.id, longitude=lon, latitude=lat, **result[0])

    await message.answer(utils.format_place(result[0]), parse_mode=types.ParseMode.HTML)


@dp.message_handler(Text(equals='Добавить новое'))
async def add_new_location(message: types.Message, state: FSMContext):
    await state.finish()

    if utils.location_list_len(message.from_user.id) > 4:
        await message.answer(
            'У вас слишком много сохраненных мест! Удалите лишьнее, чтобы дальше сохранять места!',
            reply_markup=nav.mainMenu)
        return

    await message.answer('Введите название вашего места',
                         reply_markup=ReplyKeyboardMarkup(resize_keyboard=True)
                         .add(KeyboardButton('Отменить')))

    await state.set_state(HandAdditionLocation.name.state)


@dp.message_handler(content_types=types.ContentType.TEXT, state=HandAdditionLocation.name)
async def hand_setting_name(message: types.Message, state: FSMContext):
    if message.text == 'Отменить':
        await state.finish()
        await message.answer('Действие отменено', reply_markup=nav.mainMenu)
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

    path = utils.get_project_path() + \
           f'data/imgs/{message.from_user.id}_{utils.location_list_len(message.from_user.id) + 1}.png'
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
            await message.answer('Что-то пошло не так. Попробуйте еще', reply_markup=nav.mainMenu)

        else:
            await message.answer('Сохранено!', reply_markup=nav.mainMenu)

        await state.finish()

    else:
        await message.reply('Некоректный ввод, выберите пожалуйста с клавиатуры.')


@dp.message_handler(content_types=types.ContentType.TEXT, state=HandAdditionLocation.info_)
async def hand_setting_info_(message: types.Message, state: FSMContext):
    await state.update_data(info=message.text)

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
        await message.answer('Что-то пошло не так. Попробуйте еще', reply_markup=nav.mainMenu)

    else:
        await message.answer('Сохранено!', reply_markup=nav.mainMenu)

    await state.finish()


@dp.message_handler(Text(equals='Отменить'), state=HandAdditionLocation)
async def closing(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('Действие отменено', reply_markup=nav.mainMenu)


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
    text = 'Info'
    await message.reply(text, reply_markup=nav.commands_keyboard)


@dp.message_handler(state='*')
async def all_requests(message: types.Message, state: FSMContext):
    if message.text == 'Отменить':
        await message.reply('Отмена..', reply_markup=nav.mainMenu)
        await state.finish()

    else:
        await message.answer('MainMenu', reply_markup=nav.mainMenu)
