import asyncio
import os
import logging

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

class Reg(StatesGroup):
    name = State()
    race_type = State()

load_dotenv()
bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Здравствуйте! Этот бот предназначен для записи на марафон.")

@dp.message(Command('reg'))
async def reg_first(message: Message, state: FSMContext):
    await state.set_state(Reg.name)
    await message.answer("Введите Ваше ФИО")

@dp.message(Reg.name)
async def reg_second(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Reg.race_type)
    await message.answer("Выберете тип забега (полумарафон, марафон, сверхмарафон)")

@dp.message(Reg.race_type)
async def reg_third(message: Message, state: FSMContext):
    await state.update_data(race_type=message.text)
    data = await state.get_data()
    await message.answer(f'Поздравляем, {data["name"]}, вы успешно записались на {data["race_type"]}!')
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        exit(0)