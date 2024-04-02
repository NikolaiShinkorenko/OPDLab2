import asyncio
import os
import logging
import descriptions as dsc

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (Message, ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery)
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

class Reg(StatesGroup):
    name = State()
    race_type = State()

load_dotenv()
bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher()

start_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="/reg"), KeyboardButton(text='/info')]],
    resize_keyboard=True,
    input_field_placeholder="Список доступных команд")

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
    [InlineKeyboardButton(text="Назад", callback_data='back')]])

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(dsc.START_INFO, reply_markup=start_keyboard)

@dp.message(Command('reg'))
async def reg_first(message: Message, state: FSMContext):
    await state.set_state(Reg.name)
    await message.answer("Введите Ваше ФИО")

@dp.message(Reg.name)
async def reg_second(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Reg.race_type)
    await message.answer("Выберете тип забега", reply_markup=race_types)

@dp.message(Reg.race_type)
async def reg_third(message: Message, state: FSMContext):
    if message.text in dsc.RACE_LIST:
        await state.update_data(race_type=message.text)
        data = await state.get_data()
        await message.answer(f'Поздравляем, {data["name"]}, вы успешно записались на {data["race_type"].lower()}!')
        await state.clear()
    else:
        await message.answer("Ошибка, такого варианта нет в моем списке 🥺")
    print(f'DATA:{data["name"]}/{data["race_type"]}')

@dp.message(Command('info'))
async def info(message: Message):
    await message.answer(dsc.RACE_START_INFO, reply_markup=race_info)

@dp.callback_query(F.data == 'half')
async def half(callback: CallbackQuery):
    await callback.message.edit_text(dsc.HALF_MARATHON_INFO, reply_markup=race_info_back)

@dp.callback_query(F.data == 'common')
async def common(callback: CallbackQuery):
    await callback.message.edit_text(dsc.COMMON_MARATHON_INFO, reply_markup=race_info_back)

@dp.callback_query(F.data == 'over')
async def over(callback: CallbackQuery):
    await callback.message.edit_text(dsc.OVER_MARATHON_INFO, reply_markup=race_info_back)

@dp.callback_query(F.data == 'back')
async def back(callback: CallbackQuery):
    await callback.message.edit_text(dsc.RACE_START_INFO, reply_markup=race_info)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        exit(0)