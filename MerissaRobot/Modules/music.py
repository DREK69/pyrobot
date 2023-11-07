import asyncio
import os
from typing import Callable, Union

import yt_dlp
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus, MessageEntityType
from pyrogram.errors import (
    ChatAdminRequired,
    UserAlreadyParticipant,
    UserNotParticipant,
)
from pyrogram.types import (
    Audio,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    Message,
    Voice,
)
from pytgcalls.exceptions import NoActiveGroupCall, TelegramServerError, UnMuteNeeded
from pytgcalls.types import AudioPiped, HighQualityAudio, HighQualityVideo, Update, AudioVideoPiped
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
from MerissaRobot.Utils.Helpers.permissions import adminsOnly

DURATION_LIMIT = int("90")

welcome = 20
close = 30
merissadb = {}
active = []
stream = {}


async def ytdl(link):
    proc = await asyncio.create_subprocess_exec(
        "yt-dlp",
        "-g",
        "-f",
        "best[height<=?720][width<=?1280]",
        f"{link}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if stdout:
        return 1, stdout.decode().split("\n")[0]
    else:
        return 0, stderr.decode()


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


ydl_opts = {"format": "bestaudio[ext=m4a]", "outtmpl": "downloads/%(id)s.%(ext)s"}


async def ytaudio(videoid):
    file = os.path.join("downloads", f"{videoid}.m4a")
    if os.path.exists(file):
        return file
    loop = asyncio.get_running_loop()
    link = f"https://m.youtube.com/watch?v={videoid}"
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        await loop.run_in_executor(None, ydl.download, [link])
    return file


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
    if await is_active_chat(message.chat.id):
        await put(
            message.chat.id,
            title,
            duration,
            videoid,
            file_path,
            ruser,
            message.from_user.id,
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


@pbot.on_message(filters.command("vplay") & filters.private)
async def vplay(c, m):
    await m.delete()
    if len(m.command) < 2:
        return await m.reply_text("Please enter link to Play!")
    link = m.text.split(None, 1)[1]
    if not "https" in link:
        return await m.reply_text("Please enter link to Play!")
    x = await m.reply_text("Processing...")
    await x.edit_text("Downloading...")
    shub, ytlink = await ytdl(link)
    if shub == 0:
        return await x.edit(f"❌ yt-dl issues detected\n\n» `{ytlink}`")
    await pytgcalls.join_group_call(
        -1001708378054, AudioVideoPiped(ytlink, HighQualityAudio(), HighQualityVideo())
    )
    await x.edit_text("Video Streaming Started...")


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
            await pytgcalls.leave_group_call(query.message.chat.id)
            await user.send_message(
                query.message.chat.id,
                "<b>•Music PlayBack Ended\n•Assistant Leaving This Group\n•Thanks For Using This Bot•</b>",
            )
            return await user.leave_chat(query.message.chat.id)
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
                await query.edit_message_reply_markup(
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
                await user.send_message(
                    query.message.chat.id,
                    "<b>• Music PlayBack Ended\n• Assistant Leaving This Group\n• Thanks For Using This Bot•</b>",
                )
                return await user.leave_chat(query.message.chat.id)
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
                await pytgcalls.leave_group_call(query.message.chat.id)
                await user.send_message(
                    query.message.chat.id,
                    "<b>• Music PlayBack Ended\n• Assistant Leaving This Group\n• Thanks For Using This Bot•</b>",
                )
                return await user.leave_chat(query.message.chat.id)

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
            await pytgcalls.leave_group_call(chat_id)
            await user.send_message(
                chat_id,
                "<b>•Music PlayBack Ended\n•Assistant Leaving This Group\n•Thanks For Using This Bot•</b>",
            )
            return await user.leave_chat(chat_id)
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
            await pytgcalls.leave_group_call(chat_id)
            await user.send_message(
                chat_id,
                "<b>• Music PlayBack Ended\n• Assistant Leaving This Group\n• Thanks For Using This Bot•</b>",
            )
            return await user.leave_chat(chat_id)

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
