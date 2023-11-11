from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pytgcalls.types import (
    AudioPiped,
    AudioVideoPiped,
    HighQualityAudio,
    HighQualityVideo,
    Update,
)

from MerissaRobot import BOT_ID, BOT_USERNAME, pbot, pytgcalls, user
from MerissaRobot.helpers import get_ytthumb
from MerissaRobot.Utils.Helpers.vcfunction import _clear_, merissadb

welcome = 20
close = 30


@pbot.on_message(filters.video_chat_started, group=welcome)
@pbot.on_message(filters.video_chat_ended, group=close)
async def welcome(_, message: Message):
    try:
        await _clear_(message.chat.id)
        await pytgcalls.leave_group_call(message.chat.id)
    except:
        pass


@pbot.on_message(filters.left_chat_member)
async def ub_leave(_, message: Message):
    if message.left_chat_member.id == BOT_ID:
        try:
            await _clear_(message.chat.id)
            await pytgcalls.leave_group_call(message.chat.id)
        except:
            pass
        try:
            await user.leave_chat(message.chat.id)
        except:
            pass


@pytgcalls.on_left()
@pytgcalls.on_kicked()
@pytgcalls.on_closed_voice_chat()
async def swr_handler(_, chat_id: int):
    try:
        await _clear_(chat_id)
    except:
        pass


@pytgcalls.on_stream_end()
async def on_stream_end(pytgcalls, update: Update):
    chat_id = update.chat_id

    get = merissadb.get(chat_id)
    if not get:
        try:
            await _clear_(chat_id)
            return await pytgcalls.leave_group_call(chat_id)
        except:
            return
    else:
        process = await pbot.send_message(
            chat_id=chat_id,
            text="Downloading next track from queue...",
        )
        get[0]["title"]
        get[0]["duration"]
        file_path = get[0]["file_path"]
        videoid = get[0]["videoid"]
        req_by = get[0]["req"]
        get[0]["user_id"]
        stream_type = get[0]["stream_type"]
        get.pop(0)
        thumb = await get_ytthumb(videoid)
        if stream_type == "audio":
            stream = AudioPiped(file_path, audio_parameters=HighQualityAudio())
        else:
            stream = AudioVideoPiped(file_path, HighQualityAudio(), HighQualityVideo())

        try:
            await pytgcalls.change_stream(
                chat_id,
                stream,
            )
        except:
            await _clear_(chat_id)
            return await pytgcalls.leave_group_call(chat_id)

        await process.delete()
        await pbot.send_photo(
            chat_id=chat_id,
            photo=thumb,
            caption=f"📡 Streaming Started\n\n👤Requested By:{req_by}\nℹ️ Information- [Here](https://t.me/{BOT_USERNAME}?start=info_{videoid})",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Streaming Started", callback_data="_StreaMing"
                        ),
                    ],
                    [
                        InlineKeyboardButton(text="▶️", callback_data="resume_cb"),
                        InlineKeyboardButton(text="⏸", callback_data="pause_cb"),
                        InlineKeyboardButton(text="⏯", callback_data="skip_cb"),
                        InlineKeyboardButton(text="⏹", callback_data="end_cb"),
                    ],
                ]
            ),
        )
