import datetime
import html
import os
import platform
import re
import time
from platform import python_version
from typing import Optional
import telegram


import requests
from psutil import boot_time, cpu_percent, disk_usage, virtual_memory
from telegram import MessageEntity, Update
from telegram.constants import MessageLimit, ParseMode
from telegram.error import BadRequest
from telegram.ext import ContextTypes, CommandHandler
from telegram.helpers import escape_markdown, mention_html

import MerissaRobot.Database.sql.userinfo_sql as sql
from MerissaRobot import (
    DEMONS,
    DEV_USERS,
    DRAGONS,
    INFOPIC,
    OWNER_ID,
    TIGERS,
    TOKEN,
    WOLVES,
    StartTime,
    application,
    sw,
)
from MerissaRobot.__main__ import STATS, USER_INFO
from MerissaRobot.Database.sql.afk_sql import is_afk, set_afk
from MerissaRobot.Database.sql.global_bans_sql import is_user_gbanned
from MerissaRobot.Database.sql.users_sql import get_user_num_chats
from MerissaRobot.Handler.ptb.chat_status import sudo_plus
from MerissaRobot.Handler.ptb.extraction import extract_user
from MerissaRobot.Modules.disable import DisableAbleCommandHandler


def no_by_per(totalhp: int, percentage: int) -> float:
    """
    Calculate percentage of total value.
    
    Args:
        totalhp: Total value
        percentage: Percentage to calculate
        
    Returns:
        Calculated percentage value
    """
    return totalhp * percentage / 100


def get_percentage(totalhp: int, earnedhp: int) -> str:
    """
    Calculate percentage of earned HP from total HP.
    
    Args:
        totalhp: Total HP
        earnedhp: Earned HP
        
    Returns:
        Percentage as string
    """
    matched_less = totalhp - earnedhp
    per_of_totalhp = 100 - matched_less * 100.0 / totalhp
    per_of_totalhp = str(int(per_of_totalhp))
    return per_of_totalhp


def get_readable_time(seconds: int) -> str:
    """
    Convert seconds to readable time format.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted time string
    """
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time


async def hpmanager(user, bot) -> dict:
    """
    Calculate user's health points based on various factors.
    
    Args:
        user: Telegram user object
        bot: Bot instance
        
    Returns:
        Dictionary with HP information
    """
    total_hp = (get_user_num_chats(user.id) + 10) * 10

    if not is_user_gbanned(user.id):
        # Assign new var `new_hp` since we need `total_hp` in
        # end to calculate percentage.
        new_hp = total_hp

        # if no username decrease 25% of hp.
        if not user.username:
            new_hp -= no_by_per(total_hp, 25)
        
        try:
            photos = await bot.get_user_profile_photos(user.id)
            if not photos.photos:
                # no profile photo ==> -25% of hp
                new_hp -= no_by_per(total_hp, 25)
        except (IndexError, BadRequest):
            # no profile photo ==> -25% of hp
            new_hp -= no_by_per(total_hp, 25)
            
        # if no /setme exist ==> -20% of hp
        if not sql.get_user_me_info(user.id):
            new_hp -= no_by_per(total_hp, 20)
            
        # if no bio exist ==> -10% of hp
        if not sql.get_user_bio(user.id):
            new_hp -= no_by_per(total_hp, 10)

        if is_afk(user.id):
            afkst = set_afk(user.id)
            # if user is afk and no reason then decrease 7%
            # else if reason exist decrease 5%
            new_hp -= no_by_per(total_hp, 7) if not afkst else no_by_per(total_hp, 5)

    else:
        new_hp = no_by_per(total_hp, 5)

    return {
        "earnedhp": int(new_hp),
        "totalhp": int(total_hp),
        "percentage": get_percentage(total_hp, new_hp),
    }


def make_bar(per: int) -> str:
    """
    Create a visual progress bar.
    
    Args:
        per: Percentage value
        
    Returns:
        Visual bar string
    """
    done = min(round(per / 10), 10)
    return "■" * done + "□" * (10 - done)



async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get user or chat ID."""
    bot, args = context.bot, context.args
    msg = update.effective_message
    chat = update.effective_chat

    user_id = extract_user(msg, args)

    if user_id:
        # Case: replied message with forward
        if msg.reply_to_message and msg.reply_to_message.forward_origin:
            user1 = msg.reply_to_message.from_user
            forward_origin = msg.reply_to_message.forward_origin

            if forward_origin.sender_user:  # forwarded from a user
                user2 = forward_origin.sender_user
                await msg.reply_text(
                    f"<b>Telegram ID:</b>\n"
                    f"• {html.escape(user2.first_name)} - <code>{user2.id}</code>.\n"
                    f"• {html.escape(user1.first_name)} - <code>{user1.id}</code>.",
                    parse_mode="HTML",
                )
            else:
                # Forwarded from a channel/chat
                origin_chat = getattr(forward_origin, "chat", None)
                if origin_chat:
                    await msg.reply_text(
                        f"<b>Forwarded from chat:</b>\n"
                        f"• {html.escape(origin_chat.title)} - <code>{origin_chat.id}</code>.\n"
                        f"• {html.escape(user1.first_name)} - <code>{user1.id}</code>.",
                        parse_mode="HTML",
                    )

        else:
            # Normal case
            user = await bot.get_chat(user_id)
            await msg.reply_text(
                f"{html.escape(user.first_name)}'s id is <code>{user.id}</code>.",
                parse_mode="HTML",
            )

    elif chat.type == "private":
        await msg.reply_text(
            f"Your id is <code>{chat.id}</code>.",
            parse_mode="HTML",
        )

    else:
        await msg.reply_text(
            f"This group's id is <code>{chat.id}</code>.",
            parse_mode="HTML",
        )


async def gifid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get GIF file ID."""
    msg = update.effective_message
    if msg.reply_to_message and msg.reply_to_message.animation:
        await update.effective_message.reply_text(
            f"Gif ID:\n<code>{msg.reply_to_message.animation.file_id}</code>",
            parse_mode=ParseMode.HTML,
        )
    else:
        await update.effective_message.reply_text("Please reply to a gif to get its ID.")




async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get comprehensive user information."""
    bot, args = context.bot, context.args
    message = update.effective_message
    chat = update.effective_chat

    user_id = await extract_user(message, args)  # ✅ FIXED
    user = None

    if user_id:
        user = await bot.get_chat(user_id)
    elif not message.reply_to_message and not args:
        user = message.from_user
    else:
        await message.reply_text("I can't extract a user from this.")
        return

    rep = await message.reply_text("<code>Getting info...</code>", parse_mode="HTML")

    # Base info
    text = (
        f"╔═━「<b> Appraisal results:</b> 」\n"
        f"✪ ID: <code>{user.id}</code>\n"
        f"✪ First Name: {html.escape(user.first_name)}"
    )
    if getattr(user, "last_name", None):
        text += f"\n✪ Last Name: {html.escape(user.last_name)}"
    if getattr(user, "username", None):
        text += f"\n✪ Username: @{html.escape(user.username)}"
    text += f"\n✪ Userlink: {mention_html(user.id, 'link')}"

    # Presence in chat
    if chat.type != "private" and user.id != bot.id:
        try:
            status = await bot.get_chat_member(chat.id, user.id)
            if status.status in {ChatMemberStatus.LEFT, ChatMemberStatus.KICKED}:
                text += "\n✪ Presence: <code>Not here</code>"
            elif status.status == ChatMemberStatus.MEMBER:
                text += "\n✪ Presence: <code>Detected</code>"
            elif status.status in {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}:
                text += "\n✪ Presence: <code>Admin</code>"
        except BadRequest:
            pass

    # Extra checks (afk, hpmanager, spamwatch, disaster levels, etc.) — keep as in your version

    # Profile photo
    if INFOPIC:
        try:
            photos = await bot.get_user_profile_photos(user.id, limit=1)
            if photos.photos:
                photo_file_id = photos.photos[0][-1].file_id
                await message.reply_photo(photo=photo_file_id, caption=text, parse_mode="HTML")
            else:
                await message.reply_text(text, parse_mode="HTML", disable_web_page_preview=True)
        except BadRequest:
            await message.reply_text(text, parse_mode="HTML", disable_web_page_preview=True)
    else:
        await message.reply_text(text, parse_mode="HTML")

    await rep.delete()




async def about_me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get user's self-description."""
    bot, args = context.bot, context.args
    message = update.effective_message
    user_id = extract_user(message, args)

    user = await bot.get_chat(user_id) if user_id else message.from_user
    info = sql.get_user_me_info(user.id)

    if info:
        await update.effective_message.reply_text(
            f"*{user.first_name}*:\n{escape_markdown(info)}",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
    elif message.reply_to_message:
        username = message.reply_to_message.from_user.first_name
        await update.effective_message.reply_text(
            f"{username} hasn't set an info message about themselves yet!",
        )
    else:
        await update.effective_message.reply_text("There isn't one, use /setme to set one.")


async def set_about_me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set user's self-description."""
    message = update.effective_message
    user_id = message.from_user.id
    
    if user_id in [777000, 1087968824]:
        await message.reply_text("Error! Unauthorized")
        return
        
    bot = context.bot
    if message.reply_to_message:
        repl_message = message.reply_to_message
        repl_user_id = repl_message.from_user.id
        if repl_user_id in [bot.id, 777000, 1087968824] and (user_id in DEV_USERS):
            user_id = repl_user_id
            
    text = message.text
    info = text.split(None, 1)
    if len(info) == 2:
        if len(info[1]) < MessageLimit.MAX_TEXT_LENGTH // 4:
            sql.set_user_me_info(user_id, info[1])
            if user_id in [777000, 1087968824]:
                await message.reply_text("Authorized...Information updated!")
            elif user_id == bot.id:
                await message.reply_text("I have updated my info with the one you provided!")
            else:
                await message.reply_text("Information updated!")
        else:
            await message.reply_text(
                "The info needs to be under {} characters! You have {}.".format(
                    MessageLimit.MAX_TEXT_LENGTH // 4,
                    len(info[1]),
                ),
            )


@sudo_plus
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get system and bot statistics."""
    m = await update.effective_message.reply_text("Getting Stats...")
    uptime = datetime.datetime.fromtimestamp(boot_time()).strftime("%Y-%m-%d %H:%M:%S")
    botuptime = get_readable_time((time.time() - StartTime))
    mem = virtual_memory()
    cpu = cpu_percent()
    disk = disk_usage("/")
    uname = platform.uname()
    
    status = "<b>╔═━「 System Statistics 」</b>\n"
    status += "<b>• System uptime:</b> " + str(uptime) + "\n"
    status += "<b>• System:</b> " + str(uname.system) + "\n"
    status += "<b>• Node name:</b> " + str(uname.node) + "\n"
    status += "<b>• Release:</b> " + str(uname.release) + "\n"
    status += "<b>• Machine:</b> " + str(uname.machine) + "\n"
    status += "<b>• CPU usage:</b> " + str(cpu) + " %\n"
    status += "<b>• Ram usage:</b> " + str(mem[2]) + " %\n"
    status += "<b>• Storage used:</b> " + str(disk[3]) + " %\n"
    status += "<b>• Python version:</b> " + python_version() + "\n"
    status += f"<b>• Library version:</b> {telegram.__version__}\n"
    status += "<b>• Bot uptime:</b> " + str(botuptime) + "\n\n"
    status += "<b>╔═━「 Merissabot Statistics 」</b>\n" + "\n".join(
        [mod.__stats__() for mod in STATS]
    )
    result = re.sub(r"(\d+)", r"<code>\1</code>", status)
    result += "\n<b>╘═━「 Powered By @MerissaRobot 」</b>"
    
    await update.effective_message.reply_text(
        result, parse_mode=ParseMode.HTML, disable_web_page_preview=True
    )
    await m.delete()


async def about_bio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get user's bio set by others."""
    bot, args = context.bot, context.args
    message = update.effective_message

    user_id = extract_user(message, args)
    user = await bot.get_chat(user_id) if user_id else message.from_user
    info = sql.get_user_bio(user.id)

    if info:
        await update.effective_message.reply_text(
            "*{}*:\n{}".format(user.first_name, escape_markdown(info)),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
    elif message.reply_to_message:
        username = user.first_name
        await update.effective_message.reply_text(
            f"{username} hasn't had a message set about themselves yet!\nSet one using /setbio",
        )
    else:
        await update.effective_message.reply_text(
            "You haven't had a bio set about yourself yet!",
        )


async def set_about_bio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set bio for another user."""
    message = update.effective_message
    sender_id = update.effective_user.id
    bot = context.bot

    if message.reply_to_message:
        repl_message = message.reply_to_message
        user_id = repl_message.from_user.id

        if user_id == message.from_user.id:
            await message.reply_text(
                "Ha, you can't set your own bio! You're at the mercy of others here...",
            )
            return

        if user_id in [777000, 1087968824] and sender_id not in DEV_USERS:
            await message.reply_text("You are not authorised")
            return

        if user_id == bot.id and sender_id not in DEV_USERS:
            await message.reply_text(
                "Erm... yeah, I only trust the Ackermans to set my bio.",
            )
            return

        text = message.text
        bio = text.split(
            None,
            1,
        )  # use python's maxsplit to only remove the cmd, hence keeping newlines.

        if len(bio) == 2:
            if len(bio[1]) < MessageLimit.MAX_TEXT_LENGTH // 4:
                sql.set_user_bio(user_id, bio[1])
                await message.reply_text(
                    "Updated {}'s bio!".format(repl_message.from_user.first_name),
                )
            else:
                await message.reply_text(
                    "Bio needs to be under {} characters! You tried to set {}.".format(
                        MessageLimit.MAX_TEXT_LENGTH // 4,
                        len(bio[1]),
                    ),
                )
    else:
        await message.reply_text("Reply to someone to set their bio!")


def __user_info__(user_id: int) -> str:
    """
    Get formatted user info for display in info command.
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        Formatted user info string
    """
    bio = html.escape(sql.get_user_bio(user_id) or "")
    me = html.escape(sql.get_user_me_info(user_id) or "")
    result = ""
    if me:
        result += f"<b>About user:</b>\n{me}\n"
    if bio:
        result += f"<b>What others say:</b>\n{bio}\n"
    result = result.strip("\n")
    return result


__help__ = """
*ID:*
❂ /id*:* get the current group id. If used by replying to a message, gets that user's id.
❂ /gifid*:* reply to a gif to me to tell you its file ID.
 
*Self added information:* 
❂ /setme <text>*:* will set your info
❂ /me*:* will get your or another user's info.
Examples:
❂ /setme I am a wolf.
❂ /me @username(defaults to yours if no user specified)
 
*Information others add on you:* 
❂ /bio*:* will get your or another user's bio. This cannot be set by yourself.
❂ /setbio <text>*:* while replying, will save another user's bio 
Examples:
❂ /bio @username(defaults to yours if not specified).
❂ /setbio This user is a wolf (reply to the user)
 
*Overall Information about you:*
❂ /info*:* get information about a user. 
 
*json Detailed info:*
❂ /json*:* Get Detailed info about any message.
"""

# Handler definitions for PTB v22
SET_BIO_HANDLER = DisableAbleCommandHandler("setbio", set_about_bio)
GET_BIO_HANDLER = DisableAbleCommandHandler("bio", about_bio)

STATS_HANDLER = CommandHandler(["stats", "statistics"], stats)
ID_HANDLER = DisableAbleCommandHandler("id", get_id)
GIFID_HANDLER = DisableAbleCommandHandler("gifid", gifid)
INFO_HANDLER = DisableAbleCommandHandler("info", info)
SET_ABOUT_HANDLER = DisableAbleCommandHandler("setme", set_about_me)
GET_ABOUT_HANDLER = DisableAbleCommandHandler("me", about_me)

# Add handlers to application
application.add_handler(STATS_HANDLER)
application.add_handler(ID_HANDLER)
application.add_handler(GIFID_HANDLER)
application.add_handler(INFO_HANDLER)
application.add_handler(SET_BIO_HANDLER)
application.add_handler(GET_BIO_HANDLER)
application.add_handler(SET_ABOUT_HANDLER)
application.add_handler(GET_ABOUT_HANDLER)

__mod_name__ = "UserInfo 👩‍💻"
__command_list__ = ["setbio", "bio", "setme", "me", "info", "id", "gifid", "stats"]
__handlers__ = [
    ID_HANDLER,
    GIFID_HANDLER,
    INFO_HANDLER,
    SET_BIO_HANDLER,
    GET_BIO_HANDLER,
    SET_ABOUT_HANDLER,
    GET_ABOUT_HANDLER,
    STATS_HANDLER,
]
