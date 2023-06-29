import asyncio
import os

import requests
import wget
import youtube_dl
from pyrogram import filters
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from youtube_dl.utils import DownloadError

from MerissaRobot import pbot as Client

active = []
queues = []


async def run_async(func, *args, **kwargs):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, func, *args, **kwargs)


ph_regex = r"^https:\/\/(pornhub\.com|www\.pornhub\.com)"


@Client.on_message(filters.regex(ph_regex))
async def options(c: Client, m: Message):
    id = m.text.split("=")[1]
    await m.reply_text(
        "Tap the button to continue action!",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "📥 Download",
                        callback_data=f"phubdl_{id}",
                    ),
                    InlineKeyboardButton(
                        "🎥 Watch Online",
                        callback_data=f"phubstr_{id}",
                    ),
                ],
            ],
        ),
    )


@Client.on_callback_query(filters.regex(pattern=r"phubstr"))
async def get_video(c: Client, q: CallbackQuery):
    await q.answer("Please Wait Generating Streaming Link")
    callback_data = q.data.strip()
    id = callback_data.split("_")[1]
    formats = requests.get(
        f"https://api.princexd.tech/ytinfo?link=https://www.pornhub.com/view_video.php?viewkey={id}"
    ).json()["formats"]
    row = []
    keyboards = []
    for i in formats:
        format = i["resolution"]
        dlink = i["url"]
        button = InlineKeyboardButton(format, url=dlink)
        if len(row) < 3:       
            row.append(button)    
        else:  
            keyboards.append(row)
            row = [button]
    if row:
        keyboards.append(row)

    markup = InlineKeyboardMarkup(keyboards)
    await q.edit_message_reply_markup(
        reply_markup=markup
    )


@Client.on_callback_query(filters.regex(pattern=r"phubdl"))
async def get_video(c: Client, q: CallbackQuery):
    callback_data = q.data.strip()
    id = callback_data.split("_")[1]
    url = f"https://www.pornhub.com/view_video.php?viewkey={id}"
    message = await q.message.edit(
        "Downloading Started\n\nDownloading Speed could be Slow Please wait..."
    )
    user_id = q.message.from_user.id
    if "some" in active:
        await q.message.edit("Sorry, you can only download videos at a time!")
        return
    else:
        active.append(user_id)

    opts = {
        "format": "best",
        "addmetadata": True,
        "key": "FFmpegMetadata",
        "prefer_ffmpeg": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "postprocessors": [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}],
        "outtmpl": "%(id)s.mp4",
        "logtostderr": False,
        "quiet": True,
    }
    with youtube_dl.YoutubeDL(opts) as ydl:
        try:
            await run_async(ydl.download, [url])
        except DownloadError:
            await q.message.edit("Sorry, an error occurred")
            return
    thumb = "phthumb.jpg"
    wget.download("https://te.legra.ph/file/d4e99ab7e69d796bdb124.png", thumb)
    msg = await message.edit(
        "Uploading Started\n\nUploading Speed could be Slow Plase wait..."
    )
    for file in os.listdir("."):
        if file.endswith(".mp4"):
            await Client.send_video(
                -1001708378054,
                f"{file}",
                thumb=thumb,
                width=1280,
                height=720,
                caption="The content you requested has been successfully downloaded!",
            )
            os.remove(f"{file}")
            break
        else:
            continue
    await q.message.reply_text(
        "Join Here to Watch Video - [Click Here](https://t.me/+Ow7dStIJSLViY2Y1)",
        disable_web_page_preview=True,
    )
    await msg.delete()
    active.remove(user_id)
    os.remove(thumb)
