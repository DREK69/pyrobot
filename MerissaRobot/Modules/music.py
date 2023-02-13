import os

import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputMediaAudio,
    InputTextMessageContent,
)
from pytube import YouTube
from youtubesearchpython import VideosSearch

from MerissaRobot import pbot as Client

START_BUTTONS = InlineKeyboardMarkup(
    [[InlineKeyboardButton("🔍Search YouTube", switch_inline_query_current_chat="")]]
)


@Client.on_inline_query()
async def inlinequery(client, inline_query):
    global search_yt
    search_yt = inline_query.query
    answer = []
    video = VideosSearch(search_yt, limit=10).result()
    yt_title = video["result"][0]["title"]
    yt_views = video["result"][0]["viewCount"]["short"]
    yt_duration = video["result"][0]["duration"]
    yt_publish = video["result"][0]["publishedTime"]
    yt_channel = video["result"][4]["channel"]["name"]
    global yt_link
    yt_link = video["result"][0]["link"]
    if inline_query.query == "":
        await inline_query.answer(
            results=[
                InlineQueryResultArticle(
                    title="Search any YouTube video...",
                    input_message_content=InputTextMessageContent(
                        "Search Youtube Videos..."
                    ),
                    description="Type to search!",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "Search Videos...",
                                    switch_inline_query_current_chat="",
                                )
                            ]
                        ]
                    ),
                )
            ]
        )
    elif inline_query.chat_type == inline_query.chat_type.BOT:
        for i in range(7):
            answer.append(
                InlineQueryResultArticle(
                    title=video["result"][0]["title"],
                    thumb_url=video["result"][1]["thumbnails"][0]["url"],
                    description=video["result"][0]["viewCount"]["short"],
                    input_message_content=InputTextMessageContent(
                        f"📝**Title:-** {yt_title}\n👁️‍🗨️**Views:-** {yt_views}\n⌛**Duration:-** {yt_duration}\n📅**Published:-** {yt_publish}\n📢**Published by:-** {yt_channel}\n📽️**Watch Video:-** <a href={yt_link}>Click here</a>"
                    ),
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton("🎥Watch on YouTube", url=yt_link),
                                InlineKeyboardButton(
                                    "🔍Search again", switch_inline_query_current_chat=""
                                ),
                            ],
                            [
                                InlineKeyboardButton(
                                    "📁Download", callback_data="link_down"
                                )
                            ],
                        ]
                    ),
                )
            ),
    elif inline_query.chat_type != inline_query.chat_type.BOT:
        for i in range(7):
            answer.append(
                InlineQueryResultArticle(
                    title=video["result"][0]["title"],
                    thumb_url=video["result"][1]["thumbnails"][0]["url"],
                    description=video["result"][0]["viewCount"]["short"],
                    input_message_content=InputTextMessageContent(
                        f"📝**Title:-** {yt_title}\n👁️‍🗨️**Views:-** {yt_views}\n⌛**Duration:-** {yt_duration}\n📅**Published:-** {yt_publish}\n📢**Published by:-** {yt_channel}\n📽️**Watch Video:-** <a href={yt_link}>Click here</a>"
                    ),
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton("🎥Watch on YouTube", url=yt_link),
                                InlineKeyboardButton(
                                    "🔍Search again", switch_inline_query_current_chat=""
                                ),
                            ]
                        ]
                    ),
                )
            )
    await inline_query.answer(results=answer, cache_time=1)


QUALITY_BUTTONS = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("📽️High Quality", callback_data="highest_res"),
            InlineKeyboardButton("📽️720p", callback_data="720p"),
        ],
        [
            InlineKeyboardButton("📽️Low Quality", callback_data="lowest_res"),
            InlineKeyboardButton("📽️480p", callback_data="480p"),
        ],
        [
            InlineKeyboardButton("🎵Audio", callback_data="audio"),
            InlineKeyboardButton("📽️360p", callback_data="360p"),
        ],
    ]
)

yt_regex = r"^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$"


@Client.on_message(filters.regex(yt_regex))
async def yt_download(bot, message):
    global chat_id
    chat_id = message.chat.id
    global link
    link = message.text
    search = VideosSearch(link, limit=1).result()
    data = search["result"][0]
    data["title"]
    data["link"]
    duration = data["duration"]
    reply_markup = QUALITY_BUTTONS
    await bot.send_photo(
        message.chat.id,
        photo=f"https://i.ytimg.com/vi/{data['id']}/hqdefault.jpg",
        caption=f"Select your preferred format\n\nDuration: {str(duration)}",
        reply_markup=reply_markup,
    )


@Client.on_message(filters.command(["music", "ytdl"]))
def song(client, message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    user = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"

    query = ""
    for i in message.command[1:]:
        query += " " + str(i)
    print(query)
    message.reply("🔎 Finding...")
    ydl_opts = {"format": "bestaudio[ext=m4a]"}
    try:
        search = VideosSearch(query, limit=1).result()
        data = search["result"][0]
        songname = data["title"]
        link = data["link"]
        duration = data["duration"]
        videoid = data["id"]
    except Exception as e:
        m.edit(
            "**😴 sᴏɴɢ ɴᴏᴛ ғᴏᴜɴᴅ ᴏɴ ʏᴏᴜᴛᴜʙᴇ.**\n\n» ᴍᴀʏʙᴇ ᴛᴜɴᴇ ɢᴀʟᴛɪ ʟɪᴋʜᴀ ʜᴏ, ᴩᴀᴅʜᴀɪ - ʟɪᴋʜᴀɪ ᴛᴏʜ ᴋᴀʀᴛᴀ ɴᴀʜɪ ᴛᴜ !"
        )
        print(str(e))
        return
    thumbnail = f"https://i.ytimg.com/vi/{data['id']}/hqdefault.jpg"    
    link = f"https://youtube.com/{videoid}"
    global link
    reply_markup = QUALITY_BUTTONS
    message.reply_photo(
        thumbnail,
        caption=f"Select your preferred format\n\nTitle: {songname}\nDuration: {str(duration)}",
        reply_markup=reply_markup,
    )


@Client.on_callback_query()
async def callback_query(Client, CallbackQuery):
    ## Download videos at the highest resolution
    if CallbackQuery.data == "highest_res":
        youtube_high = YouTube(link)
        high_vid = youtube_high.streams.get_highest_resolution()
        m = await CallbackQuery.edit_message_text("Downloading.")
        download_high = high_vid.download()
        m.delete()
        try:
            await Client.send_video(chat_id, download_high, caption=youtube_high.title)
            print("success")
        except Exception as error:
            await Client.send_message(chat_id, f"Error occurred:\n<i>{error}</i>")
        os.remove(download_high)
        await m.delete()
    ## Download videos at the lowest resolution
    elif CallbackQuery.data == "lowest_res":
        youtube_less = YouTube(link)
        less_vid = youtube_less.streams.get_lowest_resolution()
        m = await CallbackQuery.edit_message_text("Downloading...")
        download_less = less_vid.download()
        try:
            await Client.send_video(chat_id, download_less, caption=youtube_less.title)
        except Exception as error:
            await Client.send_message(chat_id, f"Error occurred!!\n<i>{error}</i>")
        os.remove(download_less)
        await m.delete()
    ## Download audio
    elif CallbackQuery.data == "audio":
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
    ## 480p
    elif CallbackQuery.data == "480p":
        youtube_480 = YouTube(link)
        vid_480 = youtube_480.streams.get_lowest_resolution()
        m = await CallbackQuery.edit_message_text("Downloading...")
        download_480 = vid_480.download()
        try:
            await Client.send_video(chat_id, download_480, caption=youtube_480.title)
        except Exception as error:
            await Client.send_message(chat_id, f"Error occurred!!\n<i>{error}</i>")
        os.remove(download_480)
        await m.delete()
    elif CallbackQuery.data == "link_down":
        youtube_down = YouTube(yt_link)
        vid_down = youtube_down.streams.get_lowest_resolution()
        await CallbackQuery.edit_message_text(
            f"Downloading...\n\nFile name:- {youtube_down.title}\nDuration:- {youtube_down.length}\nWatch on YouTube:- <a href={yt_link}>Click here</a>"
        )
        download_vid = vid_down.download()
        m = await CallbackQuery.edit_message_text(
            f"**Uploading to Telegram...**\n\nIf this is getting too much time,"
            f" copy `{yt_link}` and send it directly."
        )
        try:
            await CallbackQuery.edit_message_media(media=download_vid)
        except Exception as error:
            await Client.answer_callback_query(
                CallbackQuery.id, text=f"Error occurred!!\n<i>{error}</i>"
            )
        os.remove(download_vid)
