from PIL import Image
from pip._vendor import requests
import os


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
