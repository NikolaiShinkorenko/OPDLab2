import asyncio
import os
import logging
import descriptions as dsc

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import (Message, ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery)
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

class Reg(StatesGroup):
    name = State()
    race_type = State()

class Search(StatesGroup):
    check = State()

runners = {}

load_dotenv()
bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher()

start_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="/reg"), KeyboardButton(text='/info'), KeyboardButton(text='/search')]],
    resize_keyboard=True,
    input_field_placeholder="Доступные команды")

race_types = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text=dsc.RACE_LIST[0])],
    [KeyboardButton(text=dsc.RACE_LIST[1])],
    [KeyboardButton(text=dsc.RACE_LIST[2])]],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Выберете пункт меню")

race_info = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text=dsc.RACE_LIST[0], callback_data='half')],
    [InlineKeyboardButton(text=dsc.RACE_LIST[1], callback_data='common')],
    [InlineKeyboardButton(text=dsc.RACE_LIST[2], callback_data='over')]])

race_info_back = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⬅️ Назад", callback_data='back')]])

reg_cancel = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Отмена")]],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Вы можете отменить регистрацию")

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(dsc.START_INFO, reply_markup=start_keyboard)

@dp.message(Command('reg'))
async def reg_first(message: Message, state: FSMContext):
    await state.set_state(Reg.name)
    await message.answer("Введите Ваше ФИО", reply_markup=reg_cancel)

@dp.message(Reg.name)
async def reg_second(message: Message, state: FSMContext):
    if message.text == "Отмена":
        await message.answer("Вы отменили регистрацию 😕", reply_markup=start_keyboard)
        await state.clear()
    else:
        await state.update_data(name=message.text)
        await state.set_state(Reg.race_type)
        await message.answer("Выберете тип забега", reply_markup=race_types)

@dp.message(Reg.race_type)
async def reg_third(message: Message, state: FSMContext):
    if message.text in dsc.RACE_LIST:
        await state.update_data(race_type=message.text)
        data = await state.get_data()
        await message.answer(f'Поздравляем, {data["name"]}, вы успешно записались на {data["race_type"].lower()}!',
                             reply_markup=start_keyboard)
        f = open('runners.txt', 'a+')
        f.write(f'{data["name"]}:{data["race_type"]}\n')
        f.close()
        await state.clear()
    else:
        await message.answer("Ошибка, такого варианта нет в моем списке 🥺")

@dp.message(Command('search'))
async def search(message: Message, state: FSMContext):
    await state.set_state(Search.check)
    await message.answer("Введите ФИО участника, которого хотите найти")

@dp.message(Search.check)
async def search_second(message: Message, state: FSMContext):
    await state.update_data()
    file = open('runners.txt', 'r')
    for line in file:
        runners[line.split(':')[0]] = line.rstrip('\n').split(':')[1]
    file.close()
    runner = message.text
    if runner in runners.keys():
        await message.answer(f'Участник {runner} зарегистрирован на {runners[runner].lower()} ✅')
        await state.clear()
    else:
        await message.answer("В моих списках нет такого участника 🥺")
        await state.clear()

@dp.message(Command('info'))
async def info(message: Message):
    await message.answer(dsc.RACE_START_INFO, reply_markup=race_info)

@dp.callback_query(lambda callback_query: True)
async def marathon_types(callback_query: CallbackQuery):
    if callback_query.data == 'half':
        await callback_query.message.edit_text(dsc.HALF_MARATHON_INFO, reply_markup=race_info_back)
    elif callback_query.data == 'common':
        await callback_query.message.edit_text(dsc.COMMON_MARATHON_INFO, reply_markup=race_info_back)
    elif callback_query.data == 'over':
        await callback_query.message.edit_text(dsc.OVER_MARATHON_INFO, reply_markup=race_info_back)
    elif callback_query.data == 'back':
        await callback_query.message.edit_text(dsc.RACE_START_INFO, reply_markup=race_info)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        exit(0)