import asyncio
import os
import random
import string

import requests
import wget
import yt_dlp
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

y = {}


async def run_async(func, *args, **kwargs):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, func, *args, **kwargs)


ph_regex = (
    r"^((?:https?:)?\/\/)"
    r"?((?:www|m)\.)"
    r"?((?:xvideos\.com|pornhub\.com"
    r"|xhamster\.com|xnxx\.com))"
    r"(\/)([-a-zA-Z0-9()@:%_\+.~#?&//=]*)([\w\-]+)(\S+)?$"
)


@Client.on_message(filters.regex(ph_regex))
async def options(c: Client, m: Message):
    link = m.text
    ran_hash = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
    y[ran_hash] = link
    await m.reply_text(
        "Tap the button to continue action!",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "📥 Download",
                        callback_data=f"phubdl_{ran_hash}",
                    ),
                    InlineKeyboardButton(
                        "🎥 Watch Online",
                        callback_data=f"phubstr_{ran_hash}",
                    ),
                ],
            ],
        ),
    )


@Client.on_callback_query(filters.regex("^phubstr"))
async def get_video(c: Client, q: CallbackQuery):
    await q.answer("Please Wait Generating Streaming Link")
    callback_data = q.data.strip()
    ran_hash = callback_data.split("_")[1]
    link = y.get(ran_hash)
    formats = requests.get(f"https://api.princexd.tech/ytinfo?link={link}").json()[
        "formats"
    ]
    keyboards = []
    col = []
    for i in formats:
        format = i["resolution"]
        dlink = i["url"]
        button = InlineKeyboardButton(format, url=dlink)
        if len(col) < 2:
            col.append(button)
        else:
            keyboards.append(col)
            col = [button]
    if col:
        keyboards.append(col)
    markup = InlineKeyboardMarkup(keyboards)
    await q.edit_message_reply_markup(reply_markup=markup)


@Client.on_callback_query(filters.regex("^phubdl"))
async def get_video(c: Client, q: CallbackQuery):
    callback_data = q.data.strip()
    ran_hash = callback_data.split("_")[1]
    url = y.get(ran_hash)
    message = await q.message.edit(
        "Downloading Started\n\nDownloading Speed could be Slow Please wait..."
    )
    user_id = q.message.from_user.id

    if user_id in active:
        await q.message.edit("Sorry, you can only download videos at a time!")
        return
    else:
        active.append(user_id)

    opts = {}
    with yt_dlp.YoutubeDL(opts) as ydl:
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
