import os

import lyricsgenius as lg
import requests
import yt_dlp
from pyrogram import Client, filters
from pyrogram.enums import ChatAction
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaAudio,
    InputMediaPhoto,
    InputMediaVideo,
)
from pytube import YouTube

from MerissaRobot import pbot as Client
from MerissaRobot.Utils.http import http

ytregex = r"^((?:https?:)?\/\/)?((?:www|m|music)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$"


@Client.on_message(filters.regex(ytregex) & filters.private)
async def song(client, message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    user = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"
    link = message.text
    yt = YouTube(link)
    videoid = yt.video_id
    title = yt.title
    dur = yt.length
    thumbnail = await get_ytthumb(videoid)
    await message.reply_photo(
        thumbnail,
        caption=f"**Title**: {title}\n**Duration**: {dur} seconds\n\n**Select Your Preferred Format from Below**:",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🔊 Audio",
                        callback_data=f"audio {videoid}",
                    ),
                    InlineKeyboardButton("🎥 Video", callback_data=f"video {videoid}"),
                ],
                [
                    InlineKeyboardButton("🗑️ Close", callback_data="cb_close"),
                ],
            ]
        ),
    )
    os.remove(thumb)


@Client.on_message(filters.command(["music", "ytdl", "song", "video"]))
async def song(client, message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    user = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"

    query = ""
    for i in message.command[1:]:
        query += " " + str(i)
    print(query)
    search = requests.get(
        f"https://api.princexd.tech/ytsearch?query={query}&limit=50"
    ).json()
    results = f"{len(search['result'])}"
    yt = search["result"][0]
    title = yt["title"]
    dur = yt["duration"]
    videoid = yt["id"]
    link = f"https://m.youtube.com/watch?v={videoid}"
    thumbnail = await get_ytthumb(videoid)
    await message.reply_photo(
        thumbnail,
        caption=f"**Title**: {title}\n**Duration**: {dur}\nLimit = 1/{len(search['result'])}\n\n**Select Your Track from Below and Download It**:",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "⬅️ Previous",
                        callback_data=f"next|{query}|{results-1}",
                    ),
                    InlineKeyboardButton("Next ➡", callback_data=f"next|{query}|1"),
                ],
                [
                    InlineKeyboardButton(
                        "📥 Download",
                        callback_data=f"ytdown {videoid}",
                    ),
                    InlineKeyboardButton("🗑️ Close", callback_data="cb_close"),
                ],
            ]
        ),
    )


@Client.on_callback_query(filters.regex(pattern=r"next"))
async def callback_query(Client, CallbackQuery):
    callback = CallbackQuery.data.split("|")
    query = callback[1]
    page = int(callback[2])
    yt = requests.get(
        f"https://api.princexd.tech/ytsearch?query={query}&limit=50"
    ).json()["result"][page]
    title = yt["title"]
    dur = yt["duration"]
    videoid = yt["id"]
    link = f"https://m.youtube.com/watch?v={videoid}"
    thumbnail = await get_ytthumb(videoid)
    await CallbackQuery.edit_message_media(
        InputMediaPhoto(
            thumbnail,
            caption=f"**Title**: {title}\n**Duration**: {dur}\nLimit = {page}/{len(search['result'])}\n\n**Select your track from Below and Download It**:",
        ),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("⬅️", callback_data=f"next|{query}|{page-1}"),
                    InlineKeyboardButton("➡", callback_data=f"next|{query}|{page+1}"),
                ],
                [
                    InlineKeyboardButton(
                        "📥 Download",
                        callback_data=f"ytdown {videoid}",
                    ),
                    InlineKeyboardButton("🗑️ Close", callback_data="cb_close"),
                ],
            ]
        ),
    )


@Client.on_callback_query(filters.regex(pattern=r"ytdown"))
async def callback_query(Client, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    videoid = callback_data.split(None, 1)[1]
    await CallbackQuery.edit_message_reply_markup(
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🔊 Audio",
                        callback_data=f"audio {videoid}",
                    ),
                    InlineKeyboardButton("🎥 Video", callback_data=f"video {videoid}"),
                ],
                [
                    InlineKeyboardButton("🗑️ Close", callback_data="cb_close"),
                ],
            ]
        ),
    )


@Client.on_callback_query(filters.regex(pattern=r"audio"))
async def callback_query(Client, CallbackQuery):
    chatid = CallbackQuery.message.chat.id
    m = await CallbackQuery.edit_message_text(
        "Downloading Started\n\nDownload Speed could be slow. Please hold on.."
    )
    callback_data = CallbackQuery.data.strip()
    videoid = callback_data.split(None, 1)[1]
    link = f"https://m.youtube.com/watch?v={videoid}"
    ydl_opts = {"format": "bestaudio[ext=m4a]"}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(link, download=False)
        audio_file = ydl.prepare_filename(info_dict)
        ydl.process_info(info_dict)
    thumb = await CallbackQuery.message.download()
    med = InputMediaAudio(
        audio_file,
        caption=str(info_dict["title"]),
        thumb=thumb,
        title=str(info_dict["title"]),
        performer=f"{info_dict['channel']}",
        duration=int(info_dict["duration"]),
    )
    try:
        await m.edit(
            "Uploading Started\n\nUpload Speed could be slow. Please hold on.."
        )
        await Client.send_chat_action(chatid, ChatAction.UPLOAD_AUDIO)
        await CallbackQuery.edit_message_media(media=med)
    except Exception as error:
        await CallbackQuery.edit_message_text(f"Something happened!\n<i>{error}</i>")
    os.remove(thumb)
    os.remove(audio_file)


@Client.on_callback_query(filters.regex(pattern=r"video"))
async def callback_query(Client, CallbackQuery):
    chatid = CallbackQuery.message.chat.id
    m = await CallbackQuery.edit_message_text(
        "Downloading Started\n\nDownload Speed could be slow. Please hold on.."
    )
    callback_data = CallbackQuery.data.strip()
    videoid = callback_data.split(None, 1)[1]
    link = f"https://m.youtube.com/watch?v={videoid}"
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
    try:
        with yt_dlp.YoutubeDL(opts) as ytdl:
            info_dict = ytdl.extract_info(link, download=True)
    except Exception as e:
        await m.edit(f"**ғᴀɪʟᴇᴅ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ.** \n**ᴇʀʀᴏʀ :** `{str(e)}`")
        return
    download_720 = f"{info_dict['id']}.mp4"
    thumb = await CallbackQuery.message.download()
    width = CallbackQuery.message.photo.width
    height = CallbackQuery.message.photo.height
    med = InputMediaVideo(
        media=download_720,
        width=width,
        height=height,
        caption=str(info_dict["title"]),
        thumb=thumb,
        supports_streaming=True,
    )
    try:
        await m.edit(
            "Uploading Started\n\nUpload Speed could be slow. Please hold on.."
        )
        await Client.send_chat_action(chatid, ChatAction.UPLOAD_VIDEO)
        await CallbackQuery.edit_message_media(media=med)
    except Exception as error:
        await CallbackQuery.edit_message_text(f"Error occurred!!\n<i>{error}</i>")
    os.remove(thumb)
    os.remove(download_720)


@Client.on_message(filters.command("lyrics"))
async def lyrics(client, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "Give me some text to find lyrics\n\nEx. /lyrics songname"
        )
    query = message.text.split(None, 1)
    api_key = "3w1IXc4ipZ2D7Ef3g2dogPVXnr2VBeUhBqzn5Vr6D_wQVzFFsHRDo_ycV7f8hYwT"
    y = lg.Genius(
        api_key,
        skip_non_songs=True,
        excluded_terms=["(Remix)", "(Live)"],
        remove_section_headers=True,
    )
    y.verbose = False
    lyrics = y.search_song(query, get_full_info=False).lyrics
    await message.reply_text(lyrics)


async def get_ytthumb(videoid: str):
    thumb_quality = [
        "maxresdefault.jpg",  # Best quality
        "hqdefault.jpg",
        "sddefault.jpg",
        "mqdefault.jpg",
        "default.jpg",  # Worst quality
    ]
    thumb_link = "https://i.imgur.com/4LwPLai.png"
    for qualiy in thumb_quality:
        link = f"https://i.ytimg.com/vi/{videoid}/{qualiy}"
        if (await http.get(link)).status_code == 200:
            thumb_link = link
            break
    return thumb_link
