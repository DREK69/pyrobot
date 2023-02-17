import os

import wget
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaAudio
from pytube import YouTube
from youtubesearchpython import VideosSearch

from MerissaRobot import pbot as Client


@Client.on_message(filters.command(["music", "ytdl", "song"]))
def song(client, message):
    global chat_id
    chat_id = message.chat.id
    global duration
    global thumb
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
    except Exception as e:
        message.reply(
            "**😴 sᴏɴɢ ɴᴏᴛ ғᴏᴜɴᴅ ᴏɴ ʏᴏᴜᴛᴜʙᴇ.**\n\n» ᴍᴀʏʙᴇ ᴛᴜɴᴇ ɢᴀʟᴛɪ ʟɪᴋʜᴀ ʜᴏ, ᴩᴀᴅʜᴀɪ - ʟɪᴋʜᴀɪ ᴛᴏʜ ᴋᴀʀᴛᴀ ɴᴀʜɪ ᴛᴜ !"
        )
        print(str(e))
        return
    thumb = "thumbnail.jpg"
    thumbnail = f"https://i.ytimg.com/vi/{data['id']}/hqdefault.jpg"
    wget.download(thumbnail, thumb)
    message.reply_photo(
        thumbnail,
        caption=f"**Title**: {songname}\n**Duration**: {str(duration)}\n\n**Select Your Preferred Format from Below**:",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🔊 Audio", callback_data=f"audio_{link}"),
                    InlineKeyboardButton("🎥 360p", callback_data=f"360p_{link}"),
                ],
                [
                    InlineKeyboardButton("🎥 720p", callback_data=f"720p_{link}"),
                    InlineKeyboardButton("🗑️ Close", callback_data="cb_close"),
                ],
            ]
        ),
    )


@Client.on_callback_query()
async def callback_query(Client, CallbackQuery):
    ## Download audio
    if CallbackQuery.data == "audio_{link}":
        link = CallbackQuery.data.split("_")[1]
        youtube_audio = YouTube(link)
        ydl_opts = {"format": "bestaudio[ext=m4a]"}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            audio_file = ydl.prepare_filename(info_dict)
            ydl.process_info(info_dict)
        m = await CallbackQuery.edit_message_text(
            "Downloading And Uploading Started\n\nDownload And Upload Speed could be slow. Please hold on.."
        )
        title = youtube_audio.title
        dur = info_dict["duration"]
        uploader = info_dict["uploader"]
        med = InputMediaAudio(
            media=audio_file,
            caption=title,
            title=title,
            thumb=thumb,
            duration=dur,
            performer=uploader,
        )
        try:
            await CallbackQuery.edit_message_media(media=med)
        except Exception as error:
            await Client.send_message(chat_id, f"Something happened!\n<i>{error}</i>")
        os.remove(audio_file)
        os.remove(thumb)
    ## 720p
    elif CallbackQuery.data == "720p_{link}":
        link = CallbackQuery.data.split("_")[1]
        youtube_720 = YouTube(link)
        vid_720 = youtube_720.streams.get_by_resolution("720p")
        m = await CallbackQuery.edit_message_text(
            "Downloading And Uploading Started\n\nDownload And Upload Speed could be slow. Please hold on.."
        )
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
    ## 360p
    elif CallbackQuery.data == "360p_{link}":
        link = CallbackQuery.data.split("_")[1]
        youtube_360 = YouTube(link)
        vid_360 = youtube_360.streams.get_lowest_resolution()
        m = await CallbackQuery.edit_message_text(
            "Downloading And Uploading Started\n\nDownload And Upload Speed could be slow. Please hold on.."
        )
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
