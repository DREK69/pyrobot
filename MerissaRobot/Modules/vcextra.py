import os
from typing import Callable

from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from pytgcalls.types import AudioQuality, MediaStream, Update, VideoQuality

from MerissaRobot import BOT_ID, BOT_USERNAME, OWNER_ID, pbot, pytgcalls, user
from MerissaRobot.Handler.pyro.filter_groups import (
    close_group,
    vc_function,
    welcome_group,
)
from MerissaRobot.Handler.pyro.permissions import adminsOnly
from MerissaRobot.Handler.pyro.vcfunction import (
    _clear_,
    button,
    get_active_chats,
    is_active_chat,
    is_streaming,
    merissadb,
    stream_off,
    stream_on,
)


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
        else:
            return await func(_, query)

    return cb_non_admin


@pbot.on_message(
    filters.command(["pause", "resume", "end", "skip", "playlist"]) & ~filters.private,
    group=vc_function,
)
@adminsOnly("can_manage_video_chats")
async def vc_controls(_, message):
    if message.command[0] == "pause":
        try:
            await message.delete()
        except:
            pass

        if not await is_streaming(message.chat.id):
            return await message.reply_text(
                "Did you remember that you resume the stream?"
            )

        await pytgcalls.pause_stream(message.chat.id)
        await stream_off(message.chat.id)
        return await message.reply_text(
            text=f"**Stream Paused**\n\nBy: {message.from_user.mention}",
        )
    if message.command[0] == "end":
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
    if message.command[0] == "resume":
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
    if message.command[0] == "skip":
        get = merissadb.get(message.chat.id)
        try:
            await message.delete()
            get.pop(0)
        except:
            pass
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
            stream_type = get[0]["stream_type"]
            thumb = get[0]["thumb"]

            if stream_type == "audio":
                stream = MediaStream(file_path, AudioQuality.STUDIO)
            else:
                stream = MediaStream(
                    file_path, AudioQuality.STUDIO, VideoQuality.UHD_4K
                )
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
            await message.reply_photo(
                photo=thumb,
                caption=f"📡 Streaming Started\n\n👤Requested By:{req_by}\nℹ️ Information- [Here](https://t.me/{BOT_USERNAME}?start=info_{videoid})",
                reply_markup=InlineKeyboardMarkup(button),
            )
    if message.command[0] == "playlist":
        queue = merissadb.get(message.chat.id)
        if not queue:
            return await message.reply_text("Player is idle")
        m = await message.reply_text("Processing...")
        temp = []
        for t in queue:
            temp.append(t)
        now_playing = temp[0]["title"]
        by = temp[0]["req"]
        stream_type = temp[0]["stream_type"]
        msg = "**Now Playing** in {}".format(message.chat.title)
        msg += "\n- " + now_playing
        msg += "\n- Req by " + by
        msg += "\n- StreamType: " + stream_type
        temp.pop(0)
        if temp:
            msg += "\n\n"
            msg += "**In Queue**"
            for song in temp:
                name = song["title"]
                by = song["req"]
                stream_type = song["stream_type"]
                msg += f"\n- {name}"
                msg += f"\n- Req by {by}"
                msg += "\n- StreamType:" + stream_type + "\n"
        await m.edit_text(msg)


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


@pbot.on_callback_query(filters.regex("^vccb"))
@admin_check_cb
async def admin_cbs(_, query: CallbackQuery):
    callback_data = query.data.strip()
    data = callback_data.split("_")[1]
    if data == "resume":
        if await is_streaming(query.message.chat.id):
            return await query.answer(
                "Did you remember that you paused Stream?", show_alert=True
            )
        await stream_on(query.message.chat.id)
        await pytgcalls.resume_stream(query.message.chat.id)
        return await query.message.reply_text(
            text=f"**Stream Resumed**\n\nBy : {query.from_user.mention}",
        )

    elif data == "pause":
        if not await is_streaming(query.message.chat.id):
            return await query.answer(
                "Did you Remember that you resumed the Stream ?", show_alert=True
            )
        await stream_off(query.message.chat.id)
        await pytgcalls.pause_stream(query.message.chat.id)
        return await query.message.reply_text(
            text=f"**Stream Paused**\n\nBy : {query.from_user.mention}",
        )

    elif data == "end":
        try:
            await _clear_(query.message.chat.id)
            return await pytgcalls.leave_group_call(query.message.chat.id)
        except:
            pass
        return await query.message.reply_text(
            text=f"**Stream Ended**\n\nBy : {query.from_user.mention}",
        )
        await query.message.delete()

    elif data == "close":
        try:
            await query.message.delete()
        except:
            pass

    elif data == "skip":
        get = merissadb.get(query.message.chat.id)
        try:
            get.pop(0)
        except:
            pass
        if not get:
            try:
                await _clear_(query.message.chat.id)
                await pytgcalls.leave_group_call(query.message.chat.id)
                await query.message.reply_text(
                    text=f"**Stream Skipped**\n\nBy : {query.from_user.mention}",
                )
                return await query.message.delete()
            except:
                return
        else:
            await query.message.delete()
            get[0]["title"]
            get[0]["duration"]
            videoid = get[0]["videoid"]
            file_path = get[0]["file_path"]
            req_by = get[0]["req"]
            stream_type = get[0]["stream_type"]
            thumb = get[0]["thumb"]

            if stream_type == "audio":
                stream = MediaStream(file_path, AudioQuality.STUDIO)
            else:
                stream = MediaStream(
                    file_path, AudioQuality.STUDIO, VideoQuality.UHD_4K
                )
            try:
                await pytgcalls.change_stream(
                    query.message.chat.id,
                    stream,
                )
            except Exception as ex:
                LOGGER.error(ex)
                await _clear_(query.message.chat.id)
                return await pytgcalls.leave_group_call(query.message.chat.id)
            await query.message.reply_text(
                text=f"**Stream Skipped**\n\nBy : {query.from_user.mention}",
            )
            return await query.message.reply_photo(
                thumb,
                caption=f"📡 Streaming Started\n\n👤 Requested By: {req_by}\nℹ️ Information- [Here](https://t.me/{BOT_USERNAME}?start=info_{videoid})",
                reply_markup=InlineKeyboardMarkup(button),
            )


@pbot.on_callback_query(filters.regex("^vcque"))
@admin_check_cb
async def admin_quecb(_, query: CallbackQuery):
    callback_data = query.data.strip()
    data = callback_data.split("_")[1]
    track = int(callback_data.split(None, 1)[1])
    get = merissadb.get(query.message.chat.id)
    if "pnow" in data:
        try:
            get[track]["title"]
            get[track]["duration"]
            videoid = get[track]["videoid"]
            file_path = get[track]["file_path"]
            req_by = get[track]["req"]
            stream_type = get[track]["stream_type"]
            thumb = get[track]["thumb"]
            element_to_move = get.pop(track)
            get.insert(0, element_to_move)

            if stream_type == "audio":
                stream = MediaStream(file_path, audio_parameters=HighQualityAudio())
            else:
                stream = MediaStream(file_path, HighQualityAudio(), HighQualityVideo())
            try:
                await pytgcalls.change_stream(
                    query.message.chat.id,
                    stream,
                )
            except Exception as ex:
                LOGGER.error(ex)
                await _clear_(query.message.chat.id)
                return await pytgcalls.leave_group_call(query.message.chat.id)
            await query.message.edit_text(
                text=f"**Stream ForcePlayed**\n\nBy : {query.from_user.mention}",
            )
            await query.message.reply_photo(
                thumb,
                caption=f"📡 Streaming Started\n\n👤 Requested By: {req_by}\nℹ️ Information- [Here](https://t.me/{BOT_USERNAME}?start=info_{videoid})",
                reply_markup=InlineKeyboardMarkup(button),
            )
        except:
            await query.message.edit_text(
                text="Failed to Play Track",
            )
    else:
        try:
            get.pop(track)
            await query.message.edit_text(
                text=f"**Stream Deleted**\nBy : {query.from_user.mention}",
            )
        except:
            await query.message.edit_text(
                text="Failed to delete Track",
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


@pbot.on_message(filters.video_chat_started, group=welcome_group)
@pbot.on_message(filters.video_chat_ended, group=close_group)
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
    try:
        get.pop(0)
    except:
        pass
    if get:
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
        thumb = get[0]["thumb"]

        if stream_type == "audio":
            stream = MediaStream(file_path, AudioQuality.STUDIO)
        else:
            stream = MediaStream(file_path, AudioQuality.STUDIO, VideoQuality.UHD_4K)

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
            reply_markup=InlineKeyboardMarkup(button),
        )
    else:
        try:
            await _clear_(chat_id)
            return await pytgcalls.leave_group_call(chat_id)
        except:
            return
