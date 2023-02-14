from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

__all__ = ['mainMenu', 'locationMenu', 'commands_keyboard']

mainMenu = ReplyKeyboardMarkup(resize_keyboard=True)
info_btn = KeyboardButton('Что это?')
how_to_use_btn = KeyboardButton('Как пользоваться ботом?')
commands_btn = KeyboardButton('Команды')

mainMenu.add(info_btn, how_to_use_btn)
mainMenu.add(commands_btn)

locationMenu = ReplyKeyboardMarkup(resize_keyboard=True)
location_btn = KeyboardButton('Определить по геолокации')
hand_btn = KeyboardButton('Добавить новое')
back_btn = KeyboardButton('Отменить')

locationMenu.add(location_btn, hand_btn)
locationMenu.add(back_btn)

commands_keyboard = InlineKeyboardMarkup()
add_location = InlineKeyboardButton('Добавить новое местоположение', callback_data='add_location')
show_locations = InlineKeyboardButton('Показать сохраненные местоположения', callback_data='show_locations')
reset_list = InlineKeyboardButton('Удалить все сохраненные места', callback_data='reset_list')

commands_keyboard.add(add_location)
commands_keyboard.add(show_locations)
commands_keyboard.add(reset_list)




