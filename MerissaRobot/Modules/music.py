import os

import requests
import wget
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaAudio
from pytube import YouTube
from youtubesearchpython import VideosSearch

from MerissaRobot import pbot as Client


@Client.on_message(filters.command(["music", "ytdl", "song"]))
def song(client, message):
    global chat_id
    chat_id = message.chat.id
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
    thumb = "t.jpg"
    wget.download(thumbnail, thumb)
    message.reply_photo(
        thumbnail,
        caption=f"**Title**: {songname}\n**Duration**: {str(dur)}\n\n**Select Your Preferred Format from Below**:",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🔊 Audio",
                        callback_data=f"audio {videoid}|{thumb}",
                    ),
                    InlineKeyboardButton(
                        "🎥 360p", callback_data=f"360p {videoid}"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "🎥 720p", callback_data=f"720p {videoid}"
                    ),
                    InlineKeyboardButton("🗑️ Close", callback_data="cb_close"),
                ],
            ]
        ),
    )


@Client.on_callback_query(filters.regex(pattern=r"audio"))
async def callback_query(Client, CallbackQuery):
    ## Download audio
    callback_data = CallbackQuery.data.strip()
    callback = callback_data.split(None, 1)[1]
    videoid, thumb = callback.split("|")
    link = f"https://m.youtube.com/watch?v={videoid}"
    youtube_audio = YouTube(link)
    audio = youtube_audio.streams.filter(
        mime_type="audio/mp4", abr="48kbps", only_audio=True
    ).first()
    audio_file = audio.download(filename="y.mp3")
    m = await CallbackQuery.edit_message_text(
        "Downloading And Uploading Started\n\nDownload And Upload Speed could be slow. Please hold on.."
    )
    title = youtube_audio.title
    med = InputMediaAudio(media=audio_file, caption=title, title=title, thumb=thumb)
    try:
        await CallbackQuery.edit_message_media(media=med)
    except Exception as error:
        await Client.send_message(chat_id, f"Something happened!\n<i>{error}</i>")
    os.remove(audio_file)
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
    try:
        await Client.send_video(
            chat_id,
            download_360,
            caption=youtube_360.title,
            thumb=thumb,
        )
    except Exception as error:
        await Client.send_message(chat_id, f"Error occurred!!\n<i>{error}</i>")
    os.remove(download_360)
    os.remove(thumb)
    await m.delete()


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
    try:
        await Client.send_video(
            chat_id,
            download_720,
            caption=youtube_720.title,
            thumb=thumb,
        )
    except Exception as error:
        await Client.send_message(chat_id, f"Error occurred!!\n<i>{error}</i>")
    os.remove(download_720)
    os.remove(thumb)
    await m.delete()
