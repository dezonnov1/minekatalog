import asyncio

from telebot import types
from telebot.async_telebot import AsyncTeleBot

from config import Config
from database import create_tables

bot = AsyncTeleBot(Config.token)


@bot.message_handler(commands=['start'])
async def start(message: types.Message):
    ...


async def main():
    await bot.polling(none_stop=True, skip_pending=True)
    await create_tables()


asyncio.run(main())
