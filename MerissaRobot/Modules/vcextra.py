from pyrogram import filters

from MerissaRobot import pbot, pytgcalls
from MerissaRobot.helpers import get_ytthumb
from MerissaRobot.Utils.Helpers.permissions import adminsOnly
from MerissaRobot.Utils.Helpers.vcfunction import *


@pbot.on_message(filters.command(["pause"]) & filters.group)
@adminsOnly("can_manage_video_chats")
async def pause_str(_, message: Message):
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


@pbot.on_message(filters.command(["stop", "end"]) & filters.group)
@adminsOnly("can_manage_video_chats")
async def stop_str(_, message: Message):
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
async def res_str(_, message: Message):
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
async def skip_str(_, message: Message):
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
        user_id = get[0]["user_id"]
        get.pop(0)

        stream = AudioPiped(file_path, audio_parameters=HighQualityAudio())
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
        img = await gen_thumb(videoid, user_id)
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
        get.pop(0)
        thumb = await get_ytthumb(videoid)
        stream = AudioPiped(file_path, audio_parameters=HighQualityAudio())

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
            get[0]["user_id"]
            get.pop(0)
            thumb = await get_ytthumb(videoid)
            stream = AudioPiped(file_path, audio_parameters=HighQualityAudio())
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
