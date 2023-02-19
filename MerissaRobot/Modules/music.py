import os

import requests
import wget
from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaAudio,
    InputMediaVideo,
)
from pytube import YouTube
from youtubesearchpython import VideosSearch

from MerissaRobot import pbot as Client

ytregex = r"^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$"


@Client.on_message(filters.regex(ytregex))
def song(client, message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    user = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"
    query = message.text
    try:
        search = VideosSearch(query, limit=1).result()
        data = search["result"][0]
        songname = data["title"]
        data["link"]
        videoid = data["id"]
        dur = data["duration"]
    except Exception as e:
        message.reply(
            "**😴 sᴏɴɢ ɴᴏᴛ ғᴏᴜɴᴅ ᴏɴ ʏᴏᴜᴛᴜʙᴇ.**\n\n» ᴍᴀʏʙᴇ ᴛᴜɴᴇ ɢᴀʟᴛɪ ʟɪᴋʜᴀ ʜᴏ, ᴩᴀᴅʜᴀɪ - ʟɪᴋʜᴀɪ ᴛᴏʜ ᴋᴀʀᴛᴀ ɴᴀʜɪ ᴛᴜ !"
        )
        print(str(e))
        return
    yt = requests.get(
        f"https://api.princexd.tech/ytsearch?query={query}&limit=1"
    ).json()["results"][0]
    yt["channel"]["name"]
    thumbnail = yt["thumbnails"][1]["url"]
    thumb = f"{songname}.jpg"
    wget.download(thumbnail, thumb)
    message.reply_photo(
        thumbnail,
        caption=f"**Title**: {songname}\n**Duration**: {str(dur)}\n\n**Select Your Preferred Format from Below**:",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🔊 Audio",
                        callback_data=f"audio {videoid}",
                    ),
                    InlineKeyboardButton("🎥 360p", callback_data=f"360p {videoid}"),
                ],
                [
                    InlineKeyboardButton("🎥 720p", callback_data=f"720p {videoid}"),
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
    ydl_opts = {"format": "bestaudio[ext=m4a]"}
    try:
        search = VideosSearch(query, limit=1).result()
        data = search["result"][0]
        songname = data["title"]
        data["link"]
        videoid = data["id"]
        dur = data["duration"]
    except Exception as e:
        message.reply(
            "**😴 sᴏɴɢ ɴᴏᴛ ғᴏᴜɴᴅ ᴏɴ ʏᴏᴜᴛᴜʙᴇ.**\n\n» ᴍᴀʏʙᴇ ᴛᴜɴᴇ ɢᴀʟᴛɪ ʟɪᴋʜᴀ ʜᴏ, ᴩᴀᴅʜᴀɪ - ʟɪᴋʜᴀɪ ᴛᴏʜ ᴋᴀʀᴛᴀ ɴᴀʜɪ ᴛᴜ !"
        )
        print(str(e))
        return
    yt = requests.get(
        f"https://api.princexd.tech/ytsearch?query={query}&limit=1"
    ).json()["results"][0]
    yt["channel"]["name"]
    thumbnail = yt["thumbnails"][1]["url"]
    thumb = f"{songname}.jpg"
    wget.download(thumbnail, thumb)
    message.reply_photo(
        thumbnail,
        caption=f"**Title**: {songname}\n**Duration**: {str(dur)}\n\n**Select Your Preferred Format from Below**:",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🔊 Audio",
                        callback_data=f"audio {videoid}",
                    ),
                    InlineKeyboardButton("🎥 360p", callback_data=f"360p {videoid}"),
                ],
                [
                    InlineKeyboardButton("🎥 720p", callback_data=f"720p {videoid}"),
                    InlineKeyboardButton("🗑️ Close", callback_data="cb_close"),
                ],
            ]
        ),
    )
    os.remove(thumb)


@Client.on_callback_query(filters.regex(pattern=r"audio"))
async def callback_query(Client, CallbackQuery):
    ## Download audio
    callback_data = CallbackQuery.data.strip()
    videoid = callback_data.split(None, 1)[1]
    link = f"https://m.youtube.com/watch?v={videoid}"
    youtube_audio = YouTube(link)
    title = youtube_audio.title
    thumb = await CallbackQuery.message.download()
    audio = youtube_audio.streams.filter(only_audio=True).first()
    name = f"{youtube_audio.title}.mp3"
    song = audio.download(filename=name)
    m = await CallbackQuery.edit_message_text(
        "Downloading And Uploading Started\n\nDownload And Upload Speed could be slow. Please hold on.."
    )
    med = InputMediaAudio(media=song, caption=title, title=title, thumb=thumb)
    try:
        await CallbackQuery.edit_message_media(media=med)
    except Exception as error:
        await CallbackQuery.edit_message_text(f"Something happened!\n<i>{error}</i>")
    os.remove(song)
    os.remove(thumb)


@Client.on_callback_query(filters.regex(pattern=r"360p"))
async def callback_query(Client, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    videoid = callback_data.split(None, 1)[1]
    link = f"https://m.youtube.com/watch?v={videoid}"
    youtube_360 = YouTube(link)
    vid_360 = youtube_360.streams.get_lowest_resolution()
    m = await CallbackQuery.edit_message_text(
        "Downloading And Uploading Started\n\nDownload And Upload Speed could be slow. Please hold on.."
    )
    thumb = await CallbackQuery.message.download()
    width = CallbackQuery.message.photo.width
    height = CallbackQuery.message.photo.height
    download_360 = vid_360.download()
    med = InputMediaVideo(
        download_360,
        width=width,
        height=height,
        caption=youtube_360.title,
        thumb=thumb,
        supports_streaming=True,
    )
    try:
        await CallbackQuery.edit_message_media(media=med)
    except Exception as error:
        await CallbackQuery.edit_message_text(f"Error occurred!!\n<i>{error}</i>")
    os.remove(download_360)
    os.remove(thumb)


@Client.on_callback_query(filters.regex(pattern=r"720p"))
async def callback_query(Client, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    videoid = callback_data.split(None, 1)[1]
    link = f"https://m.youtube.com/watch?v={videoid}"
    youtube_720 = YouTube(link)
    vid_720 = youtube_720.streams.get_by_resolution("720p")
    m = await CallbackQuery.edit_message_text(
        "Downloading And Uploading Started\n\nDownload And Upload Speed could be slow. Please hold on.."
    )
    thumb = await CallbackQuery.message.download()
    width = CallbackQuery.message.photo.width
    height = CallbackQuery.message.photo.height
    download_720 = vid_720.download()
    med = InputMediaVideo(
        download_720,
        width=width,
        height=height,
        caption=youtube_720.title,
        thumb=thumb,
        supports_streaming=True,
    )
    try:
        await CallbackQuery.edit_message_media(media=med)
    except Exception as error:
        await CallbackQuery.edit_message_text(f"Error occurred!!\n<i>{error}</i>")
    os.remove(download_720)
    os.remove(thumb)
