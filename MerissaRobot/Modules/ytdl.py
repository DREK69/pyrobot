import os

import lyricsgenius as lg
import requests
import wget
import yt_dlp
from pyrogram import Client, filters
from pyrogram.enums import ChatAction
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaAudio,
    InputMediaVideo,
)
from pytube import YouTube

from MerissaRobot import pbot as Client

ytregex = r"^((?:https?:)?\/\/)?((?:www|m|music)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$"


@Client.on_message(filters.regex(ytregex) & filters.private)
def song(client, message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    user = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"
    link = message.text
    yt = YouTube(link)
    videoid = yt.video_id
    title = yt.title
    dur = yt.length
    thumbnail = yt.thumbnail_url
    thumb = "thumb.png"
    wget.download(thumbnail, thumb)
    message.reply_photo(
        thumbnail,
        caption=f"**Title**: {title}\n**Duration**: {str(dur)}\n\n**Select Your Preferred Format from Below**:",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🔊 Audio",
                        callback_data=f"audio {videoid}",
                    ),
                    InlineKeyboardButton("🎥 Video", callback_data=f"720p {videoid}"),
                ],
                [
                    InlineKeyboardButton("🗑️ Close", callback_data="cb_close"),
                ],
            ]
        ),
    )
    os.remove(thumb)


@Client.on_message(filters.command(["music", "ytdl", "song"]))
def song(client, message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    user = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"

    query = ""
    for i in message.command[1:]:
        query += " " + str(i)
    print(query)
    yt = requests.get(
        f"https://api.princexd.tech/ytsearch?query={query}&limit=1"
    ).json()["result"][0]
    title = yt["title"]
    dur = yt["duration"]
    videoid = yt["id"]
    link = f"https://m.youtube.com/watch?v={videoid}"
    yt = YouTube(link)
    thumbnail = yt.thumbnail_url
    thumb = "thumb.png"
    wget.download(thumbnail, thumb)
    message.reply_photo(
        thumbnail,
        caption=f"**Title**: {title}\n**Duration**: {str(dur)}\n\n**Select Your Preferred Format from Below**:",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🔊 Audio",
                        callback_data=f"audio {videoid}",
                    ),
                    InlineKeyboardButton("🎥 Video", callback_data=f"720p {videoid}"),
                ],
                [
                    InlineKeyboardButton("🗑️ Close", callback_data="cb_close"),
                ],
            ]
        ),
    )
    os.remove(thumb)


@Client.on_callback_query(filters.regex(pattern=r"audio"))
async def callback_query(Client, CallbackQuery):
    chatid = CallbackQuery.message.chat.id
    m = await CallbackQuery.edit_message_text(
        "Downloading And Uploading Started\n\nDownload And Upload Speed could be slow. Please hold on.."
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
        await Client.send_chat_action(chatid, ChatAction.UPLOAD_AUDIO)
        await CallbackQuery.edit_message_media(media=med)
    except Exception as error:
        await CallbackQuery.edit_message_text(f"Something happened!\n<i>{error}</i>")
    os.remove(thumb)
    os.remove(audio_file)


@Client.on_callback_query(filters.regex(pattern=r"720p"))
async def callback_query(Client, CallbackQuery):
    chatid = CallbackQuery.message.chat.id
    m = await CallbackQuery.edit_message_text(
        "Downloading And Uploading Started\n\nDownload And Upload Speed could be slow. Please hold on.."
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
        media=open(download_720, "rb"),
        width=width,
        height=height,
        caption=str(info_dict["title"]),
        thumb=thumb,
        supports_streaming=True,
    )
    try:
        await Client.send_chat_action(chatid, ChatAction.UPLOAD_VIDEO)
        await CallbackQuery.edit_message_media(media=med)
    except Exception as error:
        await CallbackQuery.edit_message_text(f"Error occurred!!\n<i>{error}</i>")
    os.remove(thumb)


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
