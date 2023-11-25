import asyncio
import os
import re
import textwrap
from typing import Union

import aiofiles
import aiohttp
import yt_dlp
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from pyrogram.enums import MessageEntityType
from pyrogram.types import Audio, InlineKeyboardButton, Message, Voice
from youtubesearchpython.__future__ import VideosSearch

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
    thumb,
):
    put_f = {
        "title": title,
        "duration": duration,
        "file_path": file_path,
        "videoid": videoid,
        "req": ruser,
        "user_id": user_id,
        "stream_type": stream_type,
        "thumb": thumb,
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


button = [
    [
        InlineKeyboardButton(text="▶️", callback_data="vccb_resume"),
        InlineKeyboardButton(text="⏸", callback_data="vccb_pause"),
        InlineKeyboardButton(text="🗑️", callback_data="vccb_close"),
        InlineKeyboardButton(text="⏯", callback_data="vccb_skip"),
        InlineKeyboardButton(text="⏹", callback_data="vccb_end"),
    ]
]


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


def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage


def add_corners(im):
    bigsize = (im.size[0] * 3, im.size[1] * 3)
    mask = Image.new("L", bigsize, 0)
    ImageDraw.Draw(mask).ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(im.size, Image.LANCZOS)
    mask = ImageChops.darker(mask, im.split()[-1])
    im.putalpha(mask)


async def gen_thumb(videoid):
    os.path.join(f"downloads/{videoid}.png")
    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        results = VideosSearch(url, limit=1)
        for result in (await results.next())["result"]:
            try:
                title = result["title"]
                title = re.sub("\W+", " ", title)
                title = title.title()
            except:
                title = "Unsupported Title"
            try:
                duration = result["duration"]
            except:
                duration = "Unknown"
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            try:
                result["viewCount"]["short"]
            except:
                pass
            try:
                channel = result["channel"]["name"]
            except:
                pass

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(f"thumb{videoid}.png", mode="wb")
                    await f.write(await resp.read())
                    await f.close()

        youtube = Image.open(f"thumb{videoid}.png")
        bg = Image.open("MerissaRobot/Resources/thumb.png")
        image1 = changeImageSize(1280, 720, youtube)
        image2 = image1.convert("RGBA")
        background = image2.filter(filter=ImageFilter.BoxBlur(15))
        enhancer = ImageEnhance.Brightness(background)
        background = enhancer.enhance(0.6)

        image3 = changeImageSize(1280, 720, bg)
        image5 = image3.convert("RGBA")
        Image.alpha_composite(background, image5).save(f"temp{videoid}.png")

        Xcenter = youtube.width / 2
        Ycenter = youtube.height / 2
        x1 = Xcenter - 640
        y1 = Ycenter - 640
        x2 = Xcenter + 640
        y2 = Ycenter + 640
        logo = youtube.crop((x1, y1, x2, y2))
        logo.thumbnail((550, 550), Image.ANTIALIAS)
        logo.save(f"chop{videoid}.png")
        if not os.path.isfile(f"cropped{videoid}.png"):
            im = Image.open(f"chop{videoid}.png").convert("RGBA")
            add_corners(im)
            im.save(f"cropped{videoid}.png")

        crop_img = Image.open(f"cropped{videoid}.png")
        logo = crop_img.convert("RGBA")
        logo.thumbnail((370, 370), Image.ANTIALIAS)
        int((1280 - 365) / 2)
        background = Image.open(f"temp{videoid}.png")
        background.paste(logo, (50, 150), mask=logo)
        background.paste(image3, (0, 0), mask=image3)

        draw = ImageDraw.Draw(background)
        font = ImageFont.truetype("MerissaRobot/Resources/font/font2.ttf", 45)
        arial = ImageFont.truetype("MerissaRobot/Resources/font/font.ttf", 27)

        draw.text(
            (1050, 30),
            "Merissa",
            fill="white",
            stroke_width=1,
            stroke_fill="black",
            font=ImageFont.truetype("MerissaRobot/Resources/font/font2.ttf", 28),
        )
        draw.text(
            (1075, 57),
            "Music",
            fill="rgb(170, 51, 106)",
            font=ImageFont.truetype("MerissaRobot/Resources/font/font.ttf", 20),
        )
        draw.text(
            (20, 10),
            "NOW PLAYING...",
            fill="white",
            stroke_width=2,
            stroke_fill="rgb(82, 84, 80)",
            font=ImageFont.truetype("MerissaRobot/Resources/font/font2.ttf", 30),
        )
        para = textwrap.wrap(title, width=30)
        try:
            if para[0]:
                text_w, text_h = draw.textsize(f"{para[0]}", font=font)
                draw.text(
                    ((1280 - text_w) / 1.32, 180),
                    f"{para[0]}",
                    fill="white",
                    stroke_width=1,
                    stroke_fill="black",
                    font=font,
                )
            if para[1]:
                text_w, text_h = draw.textsize(f"{para[1]}", font=font)
                draw.text(
                    ((1280 - text_w) / 1.40, 230),
                    f"{para[1]}",
                    fill="white",
                    stroke_width=1,
                    stroke_fill="black",
                    font=font,
                )
        except:
            pass
        text_w, text_h = draw.textsize(
            f"{channel}",
            font=ImageFont.truetype("MerissaRobot/Resources/font/font.ttf", 35),
        )
        draw.text(
            ((1280 - text_w) / 1.45, 295),
            f"{channel}",
            fill="white",
            stroke_width=1,
            stroke_fill="black",
            font=ImageFont.truetype("MerissaRobot/Resources/font/font.ttf", 35),
        )

        draw.text(
            (1185, 390),
            f"{duration}",
            fill="white",
            font=arial,
        )
        draw.text(
            (450, 390),
            "0:00",
            fill="white",
            font=arial,
        )
        try:
            os.remove(f"thumb{videoid}.png")
            os.remove(f"chop{videoid}.png")
            os.remove(f"cropped{videoid}.png")
            os.remove(f"temp{videoid}.png")
        except:
            pass
        background.save(f"downloads/{videoid}.png")
        return f"downloads/{videoid}.png"
    except Exception as e:
        print(str(e))
        return "https://te.legra.ph/file/3e40a408286d4eda24191.jpg"
