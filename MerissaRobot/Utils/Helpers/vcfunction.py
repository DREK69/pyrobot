import asyncio
import os
from typing import Union

import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Audio, Message, Voice
import os
import re
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps
from youtubesearchpython.__future__ import VideosSearch
import asyncio

DURATION_LIMIT = int("90")

merissadb = {}
active = []
stream = {}


async def is_active_chat(chat_id: int) -> bool:
    if chat_id not in active:
        return False
    else:
        return True


async def add_active_chat(chat_id: int):
    if chat_id not in active:
        active.append(chat_id)


async def remove_active_chat(chat_id: int):
    if chat_id in active:
        active.remove(chat_id)


async def get_active_chats() -> list:
    return active


async def is_streaming(chat_id: int) -> bool:
    run = stream.get(chat_id)
    if not run:
        return False
    return run


async def stream_on(chat_id: int):
    stream[chat_id] = True


async def stream_off(chat_id: int):
    stream[chat_id] = False


async def _clear_(chat_id):
    try:
        merissadb[chat_id] = []
        await remove_active_chat(chat_id)
    except:
        return


async def put(
    chat_id,
    title,
    duration,
    videoid,
    file_path,
    ruser,
    user_id,
    stream_type,
):
    put_f = {
        "title": title,
        "duration": duration,
        "file_path": file_path,
        "videoid": videoid,
        "req": ruser,
        "user_id": user_id,
        "stream_type": stream_type,
    }
    get = merissadb.get(chat_id)
    if get:
        merissadb[chat_id].append(put_f)
    else:
        merissadb[chat_id] = []
        merissadb[chat_id].append(put_f)


def get_url(message_1: Message) -> Union[str, None]:
    messages = [message_1]

    if message_1.reply_to_message:
        messages.append(message_1.reply_to_message)

    text = ""
    offset = None
    length = None

    for message in messages:
        if offset:
            break

        if message.entities:
            for entity in message.entities:
                if entity.type == MessageEntityType.URL:
                    text = message.text or message.caption
                    offset, length = entity.offset, entity.length
                    break

    if offset in (None,):
        return None

    return text[offset : offset + length]


def get_file_name(audio: Union[Audio, Voice]):
    return f'{audio.file_unique_id}.{audio.file_name.split(".")[-1] if not isinstance(audio, Voice) else "ogg"}'


async def ytaudio(videoid):
    file = os.path.join("downloads", f"{videoid}.m4a")
    if os.path.exists(file):
        return file
    loop = asyncio.get_running_loop()
    link = f"https://m.youtube.com/watch?v={videoid}"
    ydl_opts = {"format": "bestaudio[ext=m4a]", "outtmpl": "downloads/%(id)s.%(ext)s"}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        await loop.run_in_executor(None, ydl.download, [link])
    return file


async def ytvideo(videoid):
    file = os.path.join("downloads", f"{videoid}.mp4")
    if os.path.exists(file):
        return file
    loop = asyncio.get_running_loop()
    link = f"https://m.youtube.com/watch?v={videoid}"
    ydl_opts = {"outtmpl": "downloads/%(id)s.%(ext)s", "format": "best[ext=mp4]"}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        await loop.run_in_executor(None, ydl.download, [link])
    return file

async def gen_thumb(videoid, status):
    try:
        thumbnail_path = os.path.join( "downloads/", f"{videoid}.png")
        url = f"https://www.youtube.com/watch?v={videoid}"
        results = VideosSearch(url, limit=1)
        video_info = (await results.next())["result"][0]
        title = video_info.get("title", "Unsupported Title")
        title = re.sub("\W+", " ", title).title()
        duration = video_info.get("duration", "Unknown Mins")
        thumbnail_url = video_info["thumbnails"][0]["url"].split("?")[0]
        views = video_info.get("viewCount", {}).get("short", "Unknown Views")
        channel = video_info.get("channel", {}).get("name", "Unknown Channel")
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail_url) as resp:
                if resp.status == 200:
                    async with aiofiles.open(thumbnail_path, mode="wb") as f:
                        await f.write(await resp.read())
        youtube = Image.open(thumbnail_path)
        image1 = youtube.resize((1280, 720))
        image2 = image1.convert("RGBA")
        background = image2.filter(filter=ImageFilter.BoxBlur(30))
        enhancer = ImageEnhance.Brightness(background)
        background = enhancer.enhance(0.6)
        Xcenter = youtube.width / 2
        Ycenter = youtube.height / 2
        x1 = Xcenter - 570
        y1 = Ycenter - 250
        x2 = Xcenter + 570
        y2 = Ycenter + 250
        logo = youtube.crop((x1, y1, x2, y2))
        logo.thumbnail((1200, 550), Image.LANCZOS)
        logo = ImageOps.expand(logo, border=8, fill="white")
        background.paste(logo, (50, 100))
        draw = ImageDraw.Draw(background)
        arial = ImageFont.truetype("MerissaRobot/Utils/Resources/font/font.ttf", 30)
        font = ImageFont.truetype("MerissaRobot/Utils/Resources/font/font2.ttf", 30)
        draw.text((63, 110), f"{status}", fill="white", font=ImageFont.truetype("MerissaRobot/Utils/Resources/font/font.ttf", 25))
        draw.text((50, 50), f"Title: {title}", fill="white", font=font)
        draw.text((50, 620), f"Duration: {duration}", fill="white", font=arial)
        draw.text((950, 620), f"Views: {views}", fill="white", font=arial)
        draw.text((1010, 570), "MerissaRobot", fill="white", font=ImageFont.truetype("MerissaRobot/Utils/Resources/font/font.ttf", 25))
        background.save(thumbnail_path)
        return thumbnail_path
    except Exception as e:
        print(f"Error generating thumbnail: {e}")
        return "https://te.legra.ph/file/3e40a408286d4eda24191.jpg"