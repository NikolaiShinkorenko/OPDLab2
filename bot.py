import asyncio
import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

load_dotenv()
bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Здравствуйте! Этот бот предназначен для записи на марафон.")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())