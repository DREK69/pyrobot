import os

import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaAudio
from pytube import YouTube
from youtubesearchpython import VideosSearch

from MerissaRobot import pbot as Client

START_BUTTONS = InlineKeyboardMarkup(
    [[InlineKeyboardButton("🔍Search YouTube", switch_inline_query_current_chat="")]]
)


QUALITY_BUTTONS = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("🎵 Audio", callback_data="audio"),
            InlineKeyboardButton("📽️ 360p", callback_data="360p"),
        ],
        [
            InlineKeyboardButton("📽️ 720p", callback_data="720p"),
        ],
    ]
)


@Client.on_message(filters.command(["music", "ytdl"]))
def song(client, message):
    global link
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
        link = data["link"]
        duration = data["duration"]
        data["id"]
    except Exception as e:
        message.reply(
            "**😴 sᴏɴɢ ɴᴏᴛ ғᴏᴜɴᴅ ᴏɴ ʏᴏᴜᴛᴜʙᴇ.**\n\n» ᴍᴀʏʙᴇ ᴛᴜɴᴇ ɢᴀʟᴛɪ ʟɪᴋʜᴀ ʜᴏ, ᴩᴀᴅʜᴀɪ - ʟɪᴋʜᴀɪ ᴛᴏʜ ᴋᴀʀᴛᴀ ɴᴀʜɪ ᴛᴜ !"
        )
        print(str(e))
        return
    thumbnail = f"https://i.ytimg.com/vi/{data['id']}/hqdefault.jpg"
    reply_markup = QUALITY_BUTTONS
    message.reply_photo(
        thumbnail,
        caption=f"Select your preferred format\n\nTitle: {songname}\nDuration: {str(duration)}",
        reply_markup=reply_markup,
    )


@Client.on_callback_query()
async def callback_query(Client, CallbackQuery):
    ## Download audio
    if CallbackQuery.data == "audio":
        youtube_audio = YouTube(link)
        ydl_opts = {"format": "bestaudio[ext=m4a]"}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            audio_file = ydl.prepare_filename(info_dict)
            ydl.process_info(info_dict)
        m = await CallbackQuery.edit_message_text("Downloading...")
        title = youtube_audio.title
        med = InputMediaAudio(media=audio_file, caption=title, title=title)
        try:
            await CallbackQuery.edit_message_media(media=med)
        except Exception as error:
            await Client.send_message(chat_id, f"Something happened!\n<i>{error}</i>")
        os.remove(audio_file)
    ## 720p
    elif CallbackQuery.data == "720p":
        youtube_720 = YouTube(link)
        vid_720 = youtube_720.streams.get_by_resolution("720p")
        m = await CallbackQuery.edit_message_text("Downloading...")
        download_720 = vid_720.download()
        try:
            await Client.send_video(chat_id, download_720, caption=youtube_720.title)
        except Exception as error:
            await Client.send_message(chat_id, f"Error occurred!!\n<i>{error}</i>")
        os.remove(download_720)
        await m.delete()
    ## 360p
    elif CallbackQuery.data == "360p":
        youtube_360 = YouTube(link)
        vid_360 = youtube_360.streams.get_lowest_resolution()
        m = await CallbackQuery.edit_message_text("Downloading...")
        download_360 = vid_360.download()
        try:
            await Client.send_video(chat_id, download_360, caption=youtube_360.title)
        except Exception as error:
            await Client.send_message(chat_id, f"Error occurred!!\n<i>{error}</i>")
        os.remove(download_360)
        await m.delete()
