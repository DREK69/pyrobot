import asyncio
import os
from typing import Union

import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Audio, Message

DURATION_LIMIT = int("90")

welcome = 20
close = 30
merissadb = {}
active = []
stream = {}


async def is_active_chat(chat_id: int) -> bool:
    if chat_id not in active:
        return False
    else:
        return True


async def add_active_chat(chat_id: int):
    if chat_id not in active:
        active.append(chat_id)


async def remove_active_chat(chat_id: int):
    if chat_id in active:
        active.remove(chat_id)


async def get_active_chats() -> list:
    return active


async def is_streaming(chat_id: int) -> bool:
    run = stream.get(chat_id)
    if not run:
        return False
    return run


async def stream_on(chat_id: int):
    stream[chat_id] = True


async def stream_off(chat_id: int):
    stream[chat_id] = False


async def _clear_(chat_id):
    try:
        merissadb[chat_id] = []
        await remove_active_chat(chat_id)
    except:
        return


async def put(
    chat_id,
    title,
    duration,
    videoid,
    file_path,
    ruser,
    user_id,
):
    put_f = {
        "title": title,
        "duration": duration,
        "file_path": file_path,
        "videoid": videoid,
        "req": ruser,
        "user_id": user_id,
    }
    get = merissadb.get(chat_id)
    if get:
        merissadb[chat_id].append(put_f)
    else:
        merissadb[chat_id] = []
        merissadb[chat_id].append(put_f)


def get_url(message_1: Message) -> Union[str, None]:
    messages = [message_1]

    if message_1.reply_to_message:
        messages.append(message_1.reply_to_message)

    text = ""
    offset = None
    length = None

    for message in messages:
        if offset:
            break

        if message.entities:
            for entity in message.entities:
                if entity.type == MessageEntityType.URL:
                    text = message.text or message.caption
                    offset, length = entity.offset, entity.length
                    break

    if offset in (None,):
        return None

    return text[offset : offset + length]


def get_file_name(audio: Union[Audio, Voice]):
    return f'{audio.file_unique_id}.{audio.file_name.split(".")[-1] if not isinstance(audio, Voice) else "ogg"}'


class DurationLimitError(Exception):
    pass


class FFmpegReturnCodeError(Exception):
    pass


async def ytaudio(videoid):
    file = os.path.join("downloads", f"{videoid}.m4a")
    if os.path.exists(file):
        return file
    loop = asyncio.get_running_loop()
    link = f"https://m.youtube.com/watch?v={videoid}"
    ydl_opts = {"format": "bestaudio[ext=m4a]", "outtmpl": "downloads/%(id)s.%(ext)s"}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        await loop.run_in_executor(None, ydl.download, [link])
    return file


async def ytvideo(link):
    file = os.path.join("downloads", f"{videoid}.mp4")
    if os.path.exists(file):
        return file
    loop = asyncio.get_running_loop()
    ydl_opts = {"outtmpl": "downloads/%(id)s.%(ext)s", "format": "best[ext=mp4]"}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        await loop.run_in_executor(None, ydl.download, [link])
        info_dict = ydl.extract_info(link, download=False)
    id = info_dict["id"]
    file = f"downloads/{id}.mp4"
    return file
