import asyncio
import os
import re

from aiogram import Bot, Dispatcher
from aiogram.types import Message

token = os.environ.get("STICKER_BOT_TOKEN")

bot = Bot(token)


async def dice_handler(event: Message):
    await event.answer_dice()


async def link_handler(event: Message):
    msg_text = event.text
    link_regexp = r"(https:\/\/vk\.com\/sticker\/\d*-(\d*)-(64|128|256|512))"
    matches = re.search(link_regexp, msg_text)

    if not matches:
        print(msg_text)
        await bot.send_message(event.chat.id, "No valid links found in your message")
        return

    groups = "\n".join(matches.groups())
    await bot.send_message(event.chat.id, groups)


async def main():
    try:
        dispatcher = Dispatcher(bot)
        dispatcher.register_message_handler(dice_handler, commands={"dice"})
        dispatcher.register_message_handler(link_handler, commands={"convert"})
        await dispatcher.start_polling()
    finally:
        await bot.close()


asyncio.run(main())
