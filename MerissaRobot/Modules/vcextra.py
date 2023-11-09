from typing import Callable

from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    Message,
)
from pytgcalls.types import AudioPiped, AudioVidoePiped, HighQualityAudio, Update

from MerissaRobot import BOT_ID, BOT_USERNAME, OWNER_ID, pbot, pytgcalls
from MerissaRobot.helpers import get_ytthumb
from MerissaRobot.Utils.Helpers.permissions import adminsOnly
from MerissaRobot.Utils.Helpers.vcfunction import *


def admin_check_cb(func: Callable) -> Callable:
    async def cb_non_admin(_, query: CallbackQuery):
        if not await is_active_chat(query.message.chat.id):
            return await query.answer(
                "Bot isn't Streaming on VideoChat.", show_alert=True
            )

        try:
            check = await pbot.get_chat_member(
                query.message.chat.id, query.from_user.id
            )
        except:
            return
        if check.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
            return await query.answer(
                "You are not admin.",
                show_alert=True,
            )

        admin = (
            await pbot.get_chat_member(query.message.chat.id, query.from_user.id)
        ).privileges
        if admin.can_manage_video_chats:
            return await func(_, query)
        else:
            return await query.answer(
                "You don't have permission to Manage Videochat",
                show_alert=True,
            )

    return cb_non_admin


@pbot.on_message(filters.command(["pause"]) & filters.group)
@adminsOnly("can_manage_video_chats")
async def pause_str(_, message):
    try:
        await message.delete()
    except:
        pass

    if not await is_streaming(message.chat.id):
        return await message.reply_text("Did you remember that you resume the stream?")

    await pytgcalls.pause_stream(message.chat.id)
    await stream_off(message.chat.id)
    return await message.reply_text(
        text=f"**Stream Paused**\n\nBy: {message.from_user.mention}",
    )


@pbot.on_message(filters.command(["end"]) & filters.group)
@adminsOnly("can_manage_video_chats")
async def stop_str(_, message):
    try:
        await message.delete()
    except:
        pass
    try:
        await _clear_(message.chat.id)
        await pytgcalls.leave_group_call(message.chat.id)
    except:
        pass

    return await message.reply_text(
        text=f"**Stream Ended/Stopped**\n\nBy : {message.from_user.mention}",
    )


@pbot.on_message(filters.command(["resume"]) & filters.group)
@adminsOnly("can_manage_video_chats")
async def res_str(_, message):
    try:
        await message.delete()
    except:
        pass

    if await is_streaming(message.chat.id):
        return await message.reply_text("Did you know you resume the stream?")
    await stream_on(message.chat.id)
    await pytgcalls.resume_stream(message.chat.id)
    return await message.reply_text(
        text=f"**Stream Resumed**\n\nBy : {message.from_user.mention}",
    )


@pbot.on_message(filters.command(["skip", "next"]) & filters.group)
@adminsOnly("can_manage_video_chats")
async def skip_str(_, message):
    try:
        await message.delete()
    except:
        pass
    get = fallendb.get(message.chat.id)
    if not get:
        try:
            await _clear_(message.chat.id)
            await pytgcalls.leave_group_call(message.chat.id)
            await message.reply_text(
                text=f"**Stream Skipped**\n\nBy : {message.from_user.mention}\n\n**No more Queue Track in** {message.chat.title}, **Leaving Voicechat.**",
            )
        except:
            return
    else:
        get[0]["title"]
        get[0]["duration"]
        file_path = get[0]["file_path"]
        videoid = get[0]["videoid"]
        req_by = get[0]["req"]
        get[0]["user_id"]
        stream_type = get[0]["stream_type"]
        get.pop(0)

        if stream_type == "audio":
            stream = AudioPiped(file_path, audio_parameters=HighQualityAudio())
        else:
            stream = AudioVidoePiped(file_path)
        try:
            await pytgcalls.change_stream(
                message.chat.id,
                stream,
            )
        except:
            await _clear_(message.chat.id)
            return await pytgcalls.leave_group_call(message.chat.id)

        await message.reply_text(
            text=f"**Skipped Stream**\n\nBy : {message.from_user.mention}",
        )
        img = await get_ytthumb(videoid)
        return await message.reply_photo(
            photo=img,
            caption=f"📡 Streaming Started\n\n👤Requested By:{req_by}\nℹ️ Information- [Here](https://t.me/{BOT_USERNAME}?start=info_{videoid})",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Stream Skipped", callback_data="_StreaMing"
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
            stream = AudioVidoePiped(file_path)

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


@pbot.on_message(
    filters.command(["clearcache", "rmdownloads"]) & filters.user(OWNER_ID)
)
async def clear_misc(_, message: Message):
    try:
        await message.delete()
    except:
        pass
    downloads = os.path.realpath("downloads")
    down_dir = os.listdir(downloads)
    pth = os.path.realpath(".")
    os_dir = os.listdir(pth)

    if down_dir:
        for file in down_dir:
            os.remove(os.path.join(downloads, file))
    if os_dir:
        for lel in os.listdir(pth):
            os.system("rm -rf *.webm *.jpg *.png")
    await message.reply_text("All temp file Cleaned.")


@pbot.on_message(filters.command("activevc") & filters.user(OWNER_ID))
async def activevc(_, message: Message):
    mystic = await message.reply_text("Getting Active Videochat...")
    chats = await get_active_chats()
    text = ""
    j = 0
    for chat in chats:
        try:
            title = (await pbot.get_chat(chat)).title
        except Exception:
            title = "Private Chat"
        if (await pbot.get_chat(chat)).username:
            user = (await pbot.get_chat(chat)).username
            text += f"<b>{j + 1}.</b>  [{title}](https://t.me/{user})\n"
        else:
            text += f"<b>{j + 1}. {title}</b> [`{chat}`]\n"
        j += 1
    if not text:
        await mystic.edit_text("No active Videochat Found...")
    else:
        await mystic.edit_text(
            f"**List Active Videochat on Music Bot:**\n\n{text}",
            disable_web_page_preview=True,
        )


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


@pbot.on_callback_query(filters.regex(pattern=r"^(resume_cb|pause_cb|skip_cb|end_cb)$"))
@admin_check_cb
async def admin_cbs(_, query: CallbackQuery):
    try:
        await query.answer()
    except:
        pass

    data = query.matches[0].group(1)

    if data == "resume_cb":
        if await is_streaming(query.message.chat.id):
            return await query.answer(
                "Did you remember that you paused Stream?", show_alert=True
            )
        await stream_on(query.message.chat.id)
        await pytgcalls.resume_stream(query.message.chat.id)
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Stream Resumed", callback_data="_StreaMing"
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

    elif data == "pause_cb":
        if not await is_streaming(query.message.chat.id):
            return await query.answer(
                "Did you Remember that you resumed the Stream ?", show_alert=True
            )
        await stream_off(query.message.chat.id)
        await pytgcalls.pause_stream(query.message.chat.id)
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Stream Paused", callback_data="_StreaMing"
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

    elif data == "end_cb":
        try:
            await _clear_(query.message.chat.id)
            return await pytgcalls.leave_group_call(query.message.chat.id)
        except:
            pass
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Stream Stoped", callback_data="_StreaMing"
                        ),
                    ],
                ]
            ),
        )
        await query.message.delete()

    elif data == "skip_cb":
        get = merissadb.get(query.message.chat.id)
        if not get:
            try:
                await _clear_(query.message.chat.id)
                await pytgcalls.leave_group_call(query.message.chat.id)
                return await query.edit_message_reply_markup(
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="Stream Skipped", callback_data="_StreaMing"
                                ),
                            ],
                        ]
                    ),
                )
            except:
                return
        else:
            get[0]["title"]
            get[0]["duration"]
            videoid = get[0]["videoid"]
            file_path = get[0]["file_path"]
            req_by = get[0]["req"]
            stream_type = get[0]["stream_type"]
            get.pop(0)

            if stream_type == "audio":
                stream = AudioPiped(file_path, audio_parameters=HighQualityAudio())
            else:
                stream = AudioVidoePiped(file_path)
            thumb = await get_ytthumb(videoid)
            try:
                await pytgcalls.change_stream(
                    query.message.chat.id,
                    stream,
                )
            except Exception as ex:
                LOGGER.error(ex)
                await _clear_(query.message.chat.id)
                return await pytgcalls.leave_group_call(query.message.chat.id)

            return await query.edit_message_media(
                InputMediaPhoto(
                    thumb,
                    caption=f"📡 Streaming Started\n\n👤 Requested By: {req_by}\nℹ️ Information- [Here](https://t.me/{BOT_USERNAME}?start=info_{videoid})",
                ),
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Stream Skipped", callback_data="_StreaMing"
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


@pbot.on_callback_query(filters.regex("unban_ass"))
@admin_check_cb
async def unban_ass(_, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    chat_id, ASS_ID = callback_request.split("|")
    umm = (await pbot.get_chat_member(int(chat_id), BOT_ID)).privileges
    if umm.can_restrict_members:
        try:
            await pbot.unban_chat_member(int(chat_id), ASS_ID)
        except:
            return await CallbackQuery.answer(
                "Failed to unban Assistant",
                show_alert=True,
            )
        return await CallbackQuery.edit_message_text(
            f"{ASS_NAME} Successfully Unban assistant by {CallbackQuery.from_user.mention}.\n\nPlay Song Now..."
        )
    else:
        return await CallbackQuery.answer(
            "I dont have permission to unban user in this chat.",
            show_alert=True,
        )
