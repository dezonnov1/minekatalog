import asyncio

from telebot import types
from telebot.async_telebot import AsyncTeleBot

from config import Config
from database import create_tables, models

bot = AsyncTeleBot(Config.token)


@bot.message_handler(commands=['start'])
async def start(message: types.Message):
    await bot.reply_to(message, message.text)


async def main():
    await create_tables()
    await bot.polling(none_stop=True, skip_pending=True)


asyncio.run(main())
