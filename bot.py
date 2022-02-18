import asyncio
import os
import re
import shutil

from aiogram import Bot, Dispatcher
from aiogram.types import Message, InputFile
from selenium import webdriver
from selenium.webdriver.common.by import By

from image_utils import download_image, add_outline, convert_to_webp

token = os.environ.get("STICKER_BOT_TOKEN")

bot = Bot(token)


async def dice_handler(event: Message):
    await event.answer_dice()


async def link_handler(event: Message):
    msg_text = event.text
    # sticker_image_link_regexp = r"(https:\/\/vk\.com\/sticker\/\d*-(\d*)-(64|128|256|512))"
    link_regexp = r"(https:\/\/m\.vk\.com\/stickers/\w*)"
    matches = re.search(link_regexp, msg_text)

    if not matches:
        print(msg_text)
        await bot.send_message(event.chat.id, "No valid links found in your message")
        return

    page_link = matches.groups()[0]
    temp_directory_name = f"pack_{event.from_user.id}_{event.message_id}"
    temp_directory_path = f"./data/{temp_directory_name}"
    print(page_link)

    os.mkdir(temp_directory_path)

    options = webdriver.ChromeOptions()
    options.add_experimental_option('prefs', {'intl.accept_languages': 'ru,ru_RU'})
    driver = webdriver.Chrome("/home/arterialist/Downloads/chromedriver/chromedriver", chrome_options=options)
    driver.get(page_link)

    # async with ClientSession() as session:
    #     async with session.get(page_link) as response:
    #         page_content = await response.text()
    #         page_content = BeautifulSoup(page_content, features="html.parser")

    stickerpack_name = driver.find_element(By.CLASS_NAME, "stickers_name").text
    stickerpack_sticker_links = driver.find_elements(By.CLASS_NAME, "sticker_img")
    stickerpack_sticker_links = list(
        sorted(
            map(
                lambda img: img.get_attribute("src").replace("64", "512").replace("128", "512").replace("256", "512"), stickerpack_sticker_links
            )
        )
    )
    driver.close()

    stickerset_name: str = None
    starting_id = None

    for sticker_link in stickerpack_sticker_links:
        sticker_id = sticker_link.split("/")[-1:][0].split("-")[1]

        if not starting_id:
            starting_id = sticker_id

        png_image_path = await download_image(sticker_link, sticker_id, temp_directory_path)
        await add_outline(png_image_path)
        webp_image_path = await convert_to_webp(temp_directory_path, sticker_id, "png")
        png_sticker = InputFile(png_image_path)
        webp_sticker = InputFile(webp_image_path)

        if not stickerset_name:
            stickerset_name = f"set_{starting_id}_{event.from_user.id}_by_StickerImporterBot"
            await bot.create_new_sticker_set(event.from_user.id, stickerset_name, f"{stickerpack_name} VK by @StickerImporterBot", "😁", png_sticker)
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
