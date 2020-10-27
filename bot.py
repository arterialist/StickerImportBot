import asyncio
import os
import re
import shutil

from PIL import Image
from aiogram import Bot, Dispatcher
from aiogram.types import Message, InputFile
from pip._vendor import requests

token = os.environ.get("STICKER_BOT_TOKEN")

bot = Bot(token)


async def download_image(link: str, sticker_id: str, path: str):
    file_path = f"{path}/{sticker_id}.png"
    with open(file_path, "wb") as image_file:
        image_file.write(requests.get(link).content)

    return file_path


async def convert_to_webp(path: str, file_name: str, file_extension: str):
    image: Image.Image = Image.open(f"{path}/{file_name}.{file_extension}").convert("RGBA")
    image.save(f"{path}/{file_name}.webp", "webp")
    return f"{path}/{file_name}.webp"


async def add_outline(path: str):
    os.system(
        f"convert {os.path.abspath(path)} \( +clone -fill White -colorize 100%% -background Black -flatten -morphology Dilate Disk:10 -blur 0x1 -alpha Copy \) +swap -composite {os.path.abspath(path)}")


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

    sticker_link = matches.groups()[0]
    starting_id = int(matches.groups()[1])
    temp_directory_name = f"pack_{event.from_user.id}_{event.message_id}"
    temp_directory_path = f"./data/{temp_directory_name}"

    os.mkdir(temp_directory_path)

    for sticker_id in range(starting_id, starting_id + 42):
        image_path = await download_image(sticker_link.replace(str(starting_id), str(sticker_id)), str(sticker_id), temp_directory_path)
        await add_outline(image_path)
        image_path = await convert_to_webp(temp_directory_path, str(sticker_id), "png")

        await bot.send_sticker(event.chat.id, InputFile(image_path))
    shutil.rmtree(temp_directory_path, ignore_errors=True)


async def main():
    try:
        dispatcher = Dispatcher(bot)
        dispatcher.register_message_handler(dice_handler, commands={"dice"})
        dispatcher.register_message_handler(link_handler, commands={"convert"})
        await dispatcher.start_polling()
    finally:
        await bot.close()


asyncio.run(main())
