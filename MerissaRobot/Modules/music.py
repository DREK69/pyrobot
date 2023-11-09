import asyncio
import os

from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import (
    ChatAdminRequired,
    UserAlreadyParticipant,
    UserNotParticipant,
)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pytgcalls.exceptions import NoActiveGroupCall, TelegramServerError, UnMuteNeeded
from pytgcalls.types import AudioPiped, AudioVideoPiped, HighQualityAudio
from telegram import InlineKeyboardButton as IKB
from youtube_search import YoutubeSearch

from MerissaRobot import (
    ASS_ID,
    ASS_MENTION,
    ASS_NAME,
    ASS_USERNAME,
    BOT_ID,
    BOT_NAME,
    BOT_USERNAME,
    LOGGER,
    OWNER_ID,
    pbot,
    pytgcalls,
    user,
)
from MerissaRobot.helpers import get_ytthumb
from MerissaRobot.Utils.Helpers.vcfunction import *


@pbot.on_message(
    filters.command(["play", "play@MerissaRobot"])
    & filters.group
    & ~filters.forwarded
    & ~filters.via_bot
)
async def play(_, message: Message):
    merissa = await message.reply_text("Processing Please Wait...")
    try:
        try:
            get = await pbot.get_chat_member(message.chat.id, ASS_ID)
        except ChatAdminRequired:
            return await merissa.edit_text(
                f"I don't have permissions to invite users via link for inviting {BOT_NAME} Assistant to {message.chat.title}."
            )
        if get.status == ChatMemberStatus.BANNED:
            unban_butt = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text=f"Unban {ASS_NAME}",
                            callback_data=f"unban_ass {message.chat.id}|{ASS_ID}",
                        ),
                    ]
                ]
            )
            return await merissa.edit_text(
                text=f"{BOT_NAME} Assistant is banned in {message.chat.title}\n\nID: {ASS_ID}\nName: {ASS_MENTION}\nUsername: @{ASS_USERNAME}\n\nPlease unban the assistant and play again...",
                reply_markup=unban_butt,
            )
    except UserNotParticipant:
        if message.chat.username:
            invitelink = message.chat.username
            try:
                await user.resolve_peer(invitelink)
            except Exception as ex:
                LOGGER.error(ex)
        else:
            try:
                invitelink = await pbot.export_chat_invite_link(message.chat.id)
            except ChatAdminRequired:
                return await merissa.edit_text(
                    f"I don't have permissions to invite users via link for inviting {BOT_NAME} Assistant to {message.chat.title}."
                )
            except Exception as ex:
                return await merissa.edit_text(
                    f"Failed to Invite {BOT_NAME} Assistant to {message.chat.title}.\n\n**Reason :** `{ex}`"
                )
        if invitelink.startswith("https://t.me/+"):
            invitelink = invitelink.replace("https://t.me/+", "https://t.me/joinchat/")
        anon = await merissa.edit_text(
            f"Please Wait...\n\nInviting {ASS_NAME} to {message.chat.title}."
        )
        try:
            await user.join_chat(invitelink)
            await asyncio.sleep(2)
            await merissa.edit_text(
                f"{ASS_NAME} Joined Successfully,\n\nStarting Stream..."
            )
        except UserAlreadyParticipant:
            pass
        except Exception as ex:
            return await merissa.edit_text(
                f"Failed to Invite {BOT_NAME} Assistant to {message.chat.title}.\n\n**Reason :** `{ex}`"
            )
        try:
            await user.resolve_peer(invitelink)
        except:
            pass

    ruser = message.from_user.first_name
    audio = (
        (message.reply_to_message.audio or message.reply_to_message.voice)
        if message.reply_to_message
        else None
    )
    url = get_url(message)
    if audio:
        if round(audio.duration / 60) > DURATION_LIMIT:
            raise DurationLimitError(
                f"Sorry, Track longer than  {DURATION_LIMIT} Minutes are not allowed to play on {BOT_NAME}."
            )

        file_name = get_file_name(audio)
        title = file_name
        duration = round(audio.duration / 60)
        file_path = (
            await message.reply_to_message.download(file_name)
            if not os.path.isfile(os.path.join("downloads", file_name))
            else f"downloads/{file_name}"
        )
        thumb = "https://te.legra.ph/file/3e40a408286d4eda24191.jpg"

    elif url:
        try:
            results = YoutubeSearch(url, max_results=1).to_dict()
            title = results[0]["title"]
            duration = results[0]["duration"]
            videoid = results[0]["id"]
            thumb = await get_ytthumb(videoid)
            secmul, dur, dur_arr = 1, 0, duration.split(":")
            for i in range(len(dur_arr) - 1, -1, -1):
                dur += int(dur_arr[i]) * secmul
                secmul *= 60

        except Exception as e:
            return await merissa.edit_text(f"Something went wrong\n\n**Error :** `{e}`")

        if (dur / 60) > DURATION_LIMIT:
            return await merissa.edit_text(
                f"Sorry, Track longer than  {DURATION_LIMIT} Minutes are not allowed to play on {BOT_NAME}."
            )
        file_path = await ytaudio(videoid)
    else:
        if len(message.command) < 2:
            return await merissa.edit_text("Please enter query to Play!")
        query = message.text.split(None, 1)[1]
        try:
            results = YoutubeSearch(query, max_results=1).to_dict()
            url = f"https://youtube.com{results[0]['url_suffix']}"
            title = results[0]["title"]
            videoid = results[0]["id"]
            duration = results[0]["duration"]
            thumb = await get_ytthumb(videoid)
            secmul, dur, dur_arr = 1, 0, duration.split(":")
            for i in range(len(dur_arr) - 1, -1, -1):
                dur += int(dur_arr[i]) * secmul
                secmul *= 60

        except Exception as e:
            LOGGER.error(str(e))
            return await merissa.edit("Failed to Process Query, try again...")

        if (dur / 60) > DURATION_LIMIT:
            return await merissa.edit(
                f"Sorry, Track longer than  {DURATION_LIMIT} Minutes are not allowed to play on {BOT_NAME}."
            )
        file_path = await ytaudio(videoid)

    try:
        videoid = videoid
    except:
        videoid = "fuckitstgaudio"

    stream_type = "audio"
    if await is_active_chat(message.chat.id):
        await put(
            message.chat.id,
            title,
            duration,
            videoid,
            file_path,
            ruser,
            message.from_user.id,
            stream_type,
        )
        thumb = await get_ytthumb(videoid)
        position = len(merissadb.get(message.chat.id))
        await message.reply_photo(
            photo=thumb,
            caption=f"⏳ Added to Queue at {position}\n\n👤Requested By:{ruser}\nℹ️ Information- [Here](https://t.me/{BOT_USERNAME}?start=info_{videoid})",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Streaming Queued", callback_data="_StreaMing"
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
    else:
        stream = AudioPiped(file_path, audio_parameters=HighQualityAudio())
        try:
            await pytgcalls.join_group_call(
                message.chat.id,
                stream,
            )

        except NoActiveGroupCall:
            return await merissa.edit_text(
                "**No Active Videochat Found.**\n\nPlease make sure Videochat is started."
            )
        except TelegramServerError:
            return await merissa.edit_text(
                "Telegram having some internal Error, Please Restart the Videochat and play again."
            )
        except UnMuteNeeded:
            return await merissa.edit_text(
                f"{BOT_NAME}Assisant Muted on VideoChat,\n\nPlease Unmute {ASS_MENTION} on Videochat and play again"
            )
        await stream_on(message.chat.id)
        await add_active_chat(message.chat.id)
        await message.reply_photo(
            photo=thumb,
            caption=f"📡 Streaming Started\n\n👤Requested By: {ruser}\nℹ️ Information- [Here](https://t.me/{BOT_USERNAME}?start=info_{videoid})",
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

    return await merissa.delete()


@pbot.on_message(
    filters.command(["vplay", "vplay@MerissaRobot"])
    & filters.group
    & ~filters.forwarded
    & ~filters.via_bot
)
async def play(_, message: Message):
    merissa = await message.reply_text("Processing Please Wait...")
    try:
        try:
            get = await pbot.get_chat_member(message.chat.id, ASS_ID)
        except ChatAdminRequired:
            return await merissa.edit_text(
                f"I don't have permissions to invite users via link for inviting {BOT_NAME} Assistant to {message.chat.title}."
            )
        if get.status == ChatMemberStatus.BANNED:
            unban_butt = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text=f"Unban {ASS_NAME}",
                            callback_data=f"unban_ass {message.chat.id}|{ASS_ID}",
                        ),
                    ]
                ]
            )
            return await merissa.edit_text(
                text=f"{BOT_NAME} Assistant is banned in {message.chat.title}\n\nID: {ASS_ID}\nName: {ASS_MENTION}\nUsername: @{ASS_USERNAME}\n\nPlease unban the assistant and play again...",
                reply_markup=unban_butt,
            )
    except UserNotParticipant:
        if message.chat.username:
            invitelink = message.chat.username
            try:
                await user.resolve_peer(invitelink)
            except Exception as ex:
                LOGGER.error(ex)
        else:
            try:
                invitelink = await pbot.export_chat_invite_link(message.chat.id)
            except ChatAdminRequired:
                return await merissa.edit_text(
                    f"I don't have permissions to invite users via link for inviting {BOT_NAME} Assistant to {message.chat.title}."
                )
            except Exception as ex:
                return await merissa.edit_text(
                    f"Failed to Invite {BOT_NAME} Assistant to {message.chat.title}.\n\n**Reason :** `{ex}`"
                )
        if invitelink.startswith("https://t.me/+"):
            invitelink = invitelink.replace("https://t.me/+", "https://t.me/joinchat/")
        anon = await merissa.edit_text(
            f"Please Wait...\n\nInviting {ASS_NAME} to {message.chat.title}."
        )
        try:
            await user.join_chat(invitelink)
            await asyncio.sleep(2)
            await merissa.edit_text(
                f"{ASS_NAME} Joined Successfully,\n\nStarting Stream..."
            )
        except UserAlreadyParticipant:
            pass
        except Exception as ex:
            return await merissa.edit_text(
                f"Failed to Invite {BOT_NAME} Assistant to {message.chat.title}.\n\n**Reason :** `{ex}`"
            )
        try:
            await user.resolve_peer(invitelink)
        except:
            pass

    ruser = message.from_user.first_name
    audio = (message.reply_to_message.video) if message.reply_to_message else None
    url = get_url(message)
    if audio:
        if round(audio.duration / 60) > DURATION_LIMIT:
            raise DurationLimitError(
                f"Sorry, Track longer than  {DURATION_LIMIT} Minutes are not allowed to play on {BOT_NAME}."
            )

        file_name = get_file_name(audio)
        title = file_name
        duration = round(audio.duration / 60)
        file_path = (
            await message.reply_to_message.download(file_name)
            if not os.path.isfile(os.path.join("downloads", file_name))
            else f"downloads/{file_name}"
        )
        thumb = "https://te.legra.ph/file/3e40a408286d4eda24191.jpg"

    elif url:
        try:
            results = YoutubeSearch(url, max_results=1).to_dict()
            title = results[0]["title"]
            duration = results[0]["duration"]
            videoid = results[0]["id"]
            thumb = await get_ytthumb(videoid)
            secmul, dur, dur_arr = 1, 0, duration.split(":")
            for i in range(len(dur_arr) - 1, -1, -1):
                dur += int(dur_arr[i]) * secmul
                secmul *= 60

        except Exception as e:
            return await merissa.edit_text(f"Something went wrong\n\n**Error :** `{e}`")

        if (dur / 60) > DURATION_LIMIT:
            return await merissa.edit_text(
                f"Sorry, Track longer than  {DURATION_LIMIT} Minutes are not allowed to play on {BOT_NAME}."
            )
        file_path = await ytvideo(url)
    else:
        if len(message.command) < 2:
            return await merissa.edit_text("Please enter query to Play!")
        query = message.text.split(None, 1)[1]
        try:
            results = YoutubeSearch(query, max_results=1).to_dict()
            url = f"https://youtube.com{results[0]['url_suffix']}"
            title = results[0]["title"]
            videoid = results[0]["id"]
            duration = results[0]["duration"]
            thumb = await get_ytthumb(videoid)
            secmul, dur, dur_arr = 1, 0, duration.split(":")
            for i in range(len(dur_arr) - 1, -1, -1):
                dur += int(dur_arr[i]) * secmul
                secmul *= 60

        except Exception as e:
            LOGGER.error(str(e))
            return await merissa.edit("Failed to Process Query, try again...")

        if (dur / 60) > DURATION_LIMIT:
            return await merissa.edit(
                f"Sorry, Track longer than  {DURATION_LIMIT} Minutes are not allowed to play on {BOT_NAME}."
            )
        file_path = await ytvideo(url)

    try:
        videoid = videoid
    except:
        videoid = "fuckitstgaudio"

    stream_type = "video"
    if await is_active_chat(message.chat.id):
        await put(
            message.chat.id,
            title,
            duration,
            videoid,
            file_path,
            ruser,
            message.from_user.id,
            stream_type,
        )
        thumb = await get_ytthumb(videoid)
        position = len(merissadb.get(message.chat.id))
        await message.reply_photo(
            photo=thumb,
            caption=f"⏳ Added to Queue at {position}\n\n👤Requested By:{ruser}\nℹ️ Information- [Here](https://t.me/{BOT_USERNAME}?start=info_{videoid})",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Streaming Queued", callback_data="_StreaMing"
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
    else:
        stream = AudioVideoPiped(file_path)
        try:
            await pytgcalls.join_group_call(
                message.chat.id,
                stream,
            )

        except NoActiveGroupCall:
            return await merissa.edit_text(
                "**No Active Videochat Found.**\n\nPlease make sure Videochat is started."
            )
        except TelegramServerError:
            return await merissa.edit_text(
                "Telegram having some internal Error, Please Restart the Videochat and play again."
            )
        except UnMuteNeeded:
            return await merissa.edit_text(
                f"{BOT_NAME}Assisant Muted on VideoChat,\n\nPlease Unmute {ASS_MENTION} on Videochat and play again"
            )
        await stream_on(message.chat.id)
        await add_active_chat(message.chat.id)
        await message.reply_photo(
            photo=thumb,
            caption=f"📡 Streaming Started\n\n👤Requested By: {ruser}\nℹ️ Information- [Here](https://t.me/{BOT_USERNAME}?start=info_{videoid})",
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

    return await merissa.delete()


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


@pbot.on_message(filters.command("activevc"))
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


@pbot.on_callback_query(filters.regex("unban_ass"))
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


__help__ = """
**A Telegram Streaming bot with some useful features.**

**Few Features Here**:
- Zero lagtime Video + Audio + live stream player.
- Working Queue and Interactive Queue Checker.
- Youtube Downloader Bar.
- Download Audios/Videos from Youtube.
- Interactive UI, Fonts and Thumbnails.
"""

__mod_name__ = "Music-Bot 🎧"

__helpbtns__ = [
    [
        IKB("Setup MusicBot", callback_data="cb_setup"),
        IKB("Commands", callback_data="cb_vcmd"),
    ],
    [IKB("🔙 Back", callback_data="help_back")],
]
