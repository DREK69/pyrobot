import asyncio
import os

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

from MerissaRobot import pbot as Client
from MerissaRobot.helpers import getreq

active = []


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
                        callback_data=f"phformats_{id}",
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
    formats = await getreq(
        f"https://api.princexd.tech/ytinfo?link=https://www.pornhub.com/view_video.php?viewkey={id}"
    ).json()["formats"]
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

@Client.on_callback_query(filters.regex("^phformats"))
async def formats_query(client, callbackquery):
    await callbackquery.answer("Getting Formats..\n\nPlease Wait..", show_alert=True)
    callback_data = callbackquery.data.strip()
    id = callback_data.split("_")[1]
    link = f"https://www.pornhub.com/view_video.php?viewkey={id}"
    ytdl_opts = {"quiet": True}
    ydl = yt_dlp.YoutubeDL(ytdl_opts)
    with ydl:
        formats_available = []
        r = ydl.extract_info(link, download=False)
        for format in r["formats"]:
            try:
                str(format["format"])
            except:
                continue
            if not "dash" in str(format["format"]).lower():
                try:
                    format["format"]
                    format["filesize"]
                    format["format_id"]
                    format["ext"]
                    format["format_note"]
                except:
                    continue
                formats_available.append(
                    {
                        "format": format["format"],
                        "filesize": format["filesize"],
                        "format_id": format["format_id"],
                        "ext": format["ext"],
                        "format_note": format["format_note"],
                        "yturl": link,
                    }
                )
    keyboard = InlineKeyboard()
    done = [160, 133, 134, 135, 136, 137, 298, 299, 264, 304, 266]
    for x in formats_available:
        check = x["format"]
        if x["filesize"] is None:
            continue
        if int(x["format_id"]) not in done:
            continue
        sz = convert_bytes(x["filesize"])
        ap = check.split("-")[1]
        to = f"{ap} = {sz}"
        keyboard.row(
            InlineKeyboardButton(
                text=to,
                callback_data=f"phubdl {x['format_id']}|{id}",
            )
        )
    await callbackquery.edit_message_reply_markup(reply_markup=keyboard)

@Client.on_callback_query(filters.regex(pattern=r"phubdl"))
async def get_video(c: Client, q: CallbackQuery):
    callback_data = q.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    format_id, id = callback_request.split("|")
    url = f"https://www.pornhub.com/view_video.php?viewkey={id}"
    message = await q.message.edit(
        "Downloading Started\n\nDownloading Speed could be Slow Please wait..."
    )
    user_id = q.message.from_user.id
    if user_id in active:
        await q.message.edit("Sorry, you can only download videos at a time!")
        return
    else:
        active.append(user_id)

    formats = f"{format_id}+140"
    opts = {
        "format": formats,
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
    await Client.send_video(
        -1001708378054,
        f"{id}.mp4",
        thumb=thumb,
        width=1280,
        height=720,
        caption="The content you requested has been successfully downloaded!",
            )
    os.remove(f"{id}.mp4")
    await q.message.reply_text(
        "Join Here to Watch Video - [Click Here](https://t.me/+Ow7dStIJSLViY2Y1)",
        disable_web_page_preview=True,
    )
    await msg.delete()
    active.remove(user_id)
