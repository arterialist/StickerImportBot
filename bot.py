import asyncio
import os
import re
import shutil

from aiogram import Bot, Dispatcher
from aiogram.types import Message, InputFile

from image_utils import download_image, add_outline, convert_to_webp

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

    sticker_link = matches.groups()[0]
    starting_id = int(matches.groups()[1])
    temp_directory_name = f"pack_{event.from_user.id}_{event.message_id}"
    temp_directory_path = f"./data/{temp_directory_name}"

    os.mkdir(temp_directory_path)

    stickerset_name: str = None
    for sticker_id in range(starting_id, starting_id + 42):

        png_image_path = await download_image(sticker_link.replace(str(starting_id), str(sticker_id)), str(sticker_id), temp_directory_path)
        await add_outline(png_image_path)
        webp_image_path = await convert_to_webp(temp_directory_path, str(sticker_id), "png")
        png_sticker = InputFile(png_image_path)
        webp_sticker = InputFile(webp_image_path)

        if not stickerset_name:
            stickerset_name = f"set_{starting_id}_{event.from_user.id}_by_StickerImporterBot"
            await bot.create_new_sticker_set(event.from_user.id, stickerset_name, "Sticker pack by @StickerImporterBot", "😁", png_sticker)
        else:
            await bot.add_sticker_to_set(event.from_user.id, stickerset_name, "😁", png_sticker)

        await bot.send_sticker(event.chat.id, webp_sticker)
    shutil.rmtree(temp_directory_path, ignore_errors=True)
    await bot.send_message(event.chat.id, f"Sticker pack link: https://t.me/addstickers/{stickerset_name}")


async def main():
    try:
        dispatcher = Dispatcher(bot)
        dispatcher.register_message_handler(dice_handler, commands={"dice"})
        dispatcher.register_message_handler(link_handler, commands={"convert"})
        await dispatcher.start_polling()
    finally:
        await bot.close()


asyncio.run(main())
