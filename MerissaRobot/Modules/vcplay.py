import asyncio
import os

from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import (
    ChatAdminRequired,
    UserAlreadyParticipant,
    UserNotParticipant,
)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pytgcalls.exceptions import (
    NoActiveGroupCall,
    NoAudioSourceFound,
    TelegramServerError,
    UnMuteNeeded,
)
from pytgcalls.types import HighQualityAudio, HighQualityVideo, MediaStream
from telegram import InlineKeyboardButton as IKB
from youtubesearchpython import VideosSearch

from MerissaRobot import (
    ASS_ID,
    ASS_MENTION,
    ASS_NAME,
    ASS_USERNAME,
    BOT_NAME,
    BOT_USERNAME,
    LOGGER,
    pbot,
    pytgcalls,
    user,
)
from MerissaRobot.Handler.pyro.filter_groups import play_group
from MerissaRobot.Handler.pyro.vcfunction import (
    DURATION_LIMIT,
    add_active_chat,
    button,
    gen_thumb,
    get_file_name,
    get_url,
    is_active_chat,
    merissadb,
    put,
    stream_on,
    ytaudio,
    ytvideo,
)


@pbot.on_message(
    filters.command(["play", "vplay"])
    & ~filters.private
    & ~filters.forwarded
    & ~filters.via_bot,
    group=play_group,
)
async def play(_, message):
    merissa = await message.reply_text("🔎 Searching...")
    chat = message.chat
    chat_id = chat.id
    try:
        try:
            get = await pbot.get_chat_member(chat_id, ASS_ID)
        except ChatAdminRequired:
            return await merissa.edit_text(
                f"I don't have permissions to invite users via link for inviting {BOT_NAME} Assistant to {chat.title}."
            )
        if get.status == ChatMemberStatus.BANNED:
            unban_butt = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text=f"Unban {ASS_NAME}",
                            callback_data=f"unban_ass {chat_id}|{ASS_ID}",
                        ),
                    ]
                ]
            )
            return await merissa.edit_text(
                text=f"{BOT_NAME} Assistant is banned in {chat.title}\n\nID: {ASS_ID}\nName: {ASS_MENTION}\nUsername: @{ASS_USERNAME}\n\nPlease unban the assistant and play again...",
                reply_markup=unban_butt,
            )
    except UserNotParticipant:
        if chat.username:
            invitelink = chat.username
            try:
                await user.resolve_peer(invitelink)
            except Exception as ex:
                LOGGER.error(ex)
        else:
            try:
                invitelink = await pbot.export_chat_invite_link(chat_id)
            except ChatAdminRequired:
                return await merissa.edit_text(
                    f"I don't have permissions to invite users via link for inviting {BOT_NAME} Assistant to {chat.title}."
                )
            except Exception as ex:
                return await merissa.edit_text(
                    f"Failed to Invite {BOT_NAME} Assistant to {chat.title}.\n\n**Reason :** `{ex}`"
                )
        if invitelink.startswith("https://t.me/+"):
            invitelink = invitelink.replace("https://t.me/+", "https://t.me/joinchat/")
        anon = await merissa.edit_text(
            f"Please Wait...\n\nInviting {ASS_NAME} to {chat.title}."
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
                f"Failed to Invite {BOT_NAME} Assistant to {chat.title}.\n\n**Reason :** `{ex}`"
            )
        try:
            await user.resolve_peer(invitelink)
        except:
            pass

    ruser = message.from_user.mention
    audio = (
        (message.reply_to_message.audio or message.reply_to_message.voice)
        if message.reply_to_message
        else None
    )
    video = (message.reply_to_message.video) if message.reply_to_message else None
    url = get_url(message)
    stream_type = ""
    if message.reply_to_message:
        await merissa.edit_text("📥 Downloading...")
        if audio:
            if round(audio.duration / 60) > DURATION_LIMIT:
                raise DurationLimitError(
                    f"Sorry, Track longer than  {DURATION_LIMIT} Minutes are not allowed to play on {BOT_NAME}."
                )

            file_name = get_file_name(audio)
            title = file_name
            duration = round(audio.duration / 60)
            videoid = "videoidhotitodedeta"
            if not os.path.isfile(os.path.join("downloads", title)):
                file_path = await message.reply_to_message.download(title)
            else:
                file_path = f"downloads/{title}"

        if video:
            if round(video.duration / 60) > DURATION_LIMIT:
                raise DurationLimitError(
                    f"Sorry, Track longer than  {DURATION_LIMIT} Minutes are not allowed to play on {BOT_NAME}."
                )

            file_name = get_file_name(video)
            title = file_name
            duration = round(video.duration / 60)
            videoid = "videoidhotitodedeta"
            if not os.path.isfile(os.path.join("downloads", title)):
                file_path = await message.reply_to_message.download(title)
            else:
                file_path = f"downloads/{title}"

        thumb = "https://te.legra.ph/file/3e40a408286d4eda24191.jpg"
        if "v" in message.command[0]:
            stream_type += "video"
        else:
            stream_type += "audio"

    elif url:
        if not "youtu" in url:
            return await merissa.edit_text("Only Youtube link Works")
        else:
            results = VideosSearch(url, limit=1).result()
            yt = results["result"][0]
            title = yt["title"]
            duration = yt["duration"]
            videoid = yt["id"]
            secmul, dur, dur_arr = 1, 0, duration.split(":")
            for i in range(len(dur_arr) - 1, -1, -1):
                dur += int(dur_arr[i]) * secmul
                secmul *= 60

            if (dur / 60) > DURATION_LIMIT:
                return await merissa.edit_text(
                    f"Sorry, Track longer than  {DURATION_LIMIT} Minutes are not allowed to play on {BOT_NAME}."
                )
            await merissa.edit_text("📥 Downloading...")
            if "v" in message.command[0]:
                file_path = await ytvideo(videoid)
                stream_type += "video"
            else:
                file_path = await ytaudio(videoid)
                stream_type += "audio"

    else:
        if len(message.command) < 2:
            return await merissa.edit_text("Please enter query to Play!")
        query = message.text.split(None, 1)[1]
        try:
            vidinfo = VideosSearch(query, limit=1).result()
            yt = vidinfo["result"][0]
            title = yt["title"]
            duration = yt["duration"]
            videoid = yt["id"]
            url = f"https://m.youtube.com/watch?v={videoid}"
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
        await merissa.edit_text("📥 Downloading...")
        if "v" in message.command[0]:
            file_path = await ytvideo(videoid)
            stream_type += "video"
        else:
            file_path = await ytaudio(videoid)
            stream_type += "audio"

    thumb = await gen_thumb(videoid)

    await put(
        chat_id,
        title,
        duration,
        videoid,
        file_path,
        ruser,
        message.from_user.id,
        stream_type,
        thumb,
    )
    if await is_active_chat(chat_id):
        position = len(merissadb.get(chat_id)) - 1
        await message.reply_text(
            f"⏳ Added to Queue at {position}\n\n🎧 Title: {title[:25]}\n👤 Requested By:{ruser}\nℹ️ Information- [Here](https://t.me/{BOT_USERNAME}?start=info_{videoid})",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="▶️ Play Now", callback_data=f"vcque_pnow {position}"
                        ),
                        InlineKeyboardButton(
                            text="❌ Delete", callback_data=f"vcque_del {position}"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="🗑️ Close", callback_data=f"vccb_close"
                        )
                    ],
                ]
            ),
            disable_web_page_preview=True,
        )
    else:
        if stream_type == "audio":
            stream = MediaStream(file_path, HighQualityAudio())
        else:
            stream = MediaStream(file_path, HighQualityAudio(), HighQualityVideo())
        await merissa.edit_text("🎧 VideoChat Joining...")
        try:
            await pytgcalls.join_group_call(
                chat_id,
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
        except NoAudioSourceFound:
            return await merissa.edit_text("M3u8 Link Not Supported.")
        except UnMuteNeeded:
            return await merissa.edit_text(
                f"{BOT_NAME} Assisant Muted on VideoChat,\n\nPlease Unmute {ASS_MENTION} on Videochat and play again"
            )
        await stream_on(chat_id)
        await add_active_chat(chat_id)
        await message.reply_photo(
            photo=thumb,
            caption=f"📡 Streaming Started\n\n👤Requested By: {ruser}\nℹ️ Information- [Here](https://t.me/{BOT_USERNAME}?start=info_{videoid})",
            reply_markup=InlineKeyboardMarkup(button),
        )

    return await merissa.delete()


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
