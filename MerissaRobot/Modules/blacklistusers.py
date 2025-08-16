# Module to blacklist users and prevent them from using commands by @TheRealPhoenix
import html
from typing import Optional

from telegram import Update
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.ext import ContextTypes, CommandHandler
from telegram.helpers import mention_html

import MerissaRobot.Database.sql.blacklistusers_sql as sql
from MerissaRobot import (
    DEMONS,
    DEV_USERS,
    DRAGONS,
    OWNER_ID,
    TIGERS,
    WOLVES,
    application,
)
from MerissaRobot.Handler.ptb.chat_status import dev_plus
from MerissaRobot.Handler.ptb.extraction import extract_user, extract_user_and_text
from MerissaRobot.Modules.log_channel import gloggable

BLACKLISTWHITELIST = [OWNER_ID] + DEV_USERS + DRAGONS + WOLVES + DEMONS
BLABLEUSERS = [OWNER_ID] + DEV_USERS


@dev_plus
@gloggable
async def bl_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Blacklist a user from using bot commands"""
    message = update.effective_message
    user = update.effective_user
    bot, args = context.bot, context.args
    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        await message.reply_text("I doubt that's a user.")
        return ""

    if user_id == bot.id:
        await message.reply_text("How am I supposed to do my work if I am ignoring myself?")
        return ""

    if user_id in BLACKLISTWHITELIST:
        await message.reply_text("No!\nNoticing Disasters is my job.")
        return ""

    try:
        target_user = await bot.get_chat(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            await message.reply_text("I can't seem to find this user.")
            return ""
        raise

    sql.blacklist_user(user_id, reason)
    await message.reply_text("I shall ignore the existence of this user!")
    
    log_message = (
        f"#BLACKLIST\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>User:</b> {mention_html(target_user.id, html.escape(target_user.first_name))}"
    )
    if reason:
        log_message += f"\n<b>Reason:</b> {html.escape(reason)}"

    return log_message


@dev_plus
@gloggable
async def unbl_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Remove a user from blacklist"""
    message = update.effective_message
    user = update.effective_user
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)

    if not user_id:
        await message.reply_text("I doubt that's a user.")
        return ""

    if user_id == bot.id:
        await message.reply_text("I always notice myself.")
        return ""

    try:
        target_user = await bot.get_chat(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            await message.reply_text("I can't seem to find this user.")
            return ""
        raise

    if sql.is_user_blacklisted(user_id):
        sql.unblacklist_user(user_id)
        await message.reply_text("*notices user*")
        log_message = (
            f"#UNBLACKLIST\n"
            f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            f"<b>User:</b> {mention_html(target_user.id, html.escape(target_user.first_name))}"
        )

        return log_message
    
    await message.reply_text("I am not ignoring them at all though!")
    return ""


@dev_plus
async def bl_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all blacklisted users"""
    users = []
    bot = context.bot
    
    for each_user in sql.BLACKLIST_USERS:
        try:
            user = await bot.get_chat(each_user)
            reason = sql.get_reason(each_user)

            if reason:
                users.append(
                    f"• {mention_html(user.id, html.escape(user.first_name))} :- {html.escape(reason)}",
                )
            else:
                users.append(f"• {mention_html(user.id, html.escape(user.first_name))}")
        except BadRequest:
            # User might be deleted or inaccessible
            reason = sql.get_reason(each_user)
            if reason:
                users.append(f"• User ID {each_user} :- {html.escape(reason)}")
            else:
                users.append(f"• User ID {each_user}")

    message = "<b>Blacklisted Users</b>\n"
    if not users:
        message += "No one is being ignored as of yet."
    else:
        message += "\n".join(users)

    await update.effective_message.reply_text(message, parse_mode=ParseMode.HTML)


async def __user_info__(user_id):
    """Return blacklist status for user info"""
    is_blacklisted = sql.is_user_blacklisted(user_id)

    text = "Blacklisted: <b>{}</b>"
    
    # Skip system users and bot itself
    if user_id in [777000, 1087968824]:
        return ""
    
    # Get bot ID asynchronously if needed
    try:
        bot_id = application.bot.id
        if user_id == bot_id:
            return ""
    except AttributeError:
        # Fallback if bot not initialized yet
        pass
    
    # Skip privileged users
    if int(user_id) in DRAGONS + TIGERS + WOLVES:
        return ""
    
    if is_blacklisted:
        text = text.format("Yes")
        reason = sql.get_reason(user_id)
        if reason:
            text += f"\nReason: <code>{html.escape(reason)}</code>"
    else:
        text = text.format("No")

    return text


def __user_info_sync__(user_id):
    """Synchronous wrapper for backward compatibility"""
    import asyncio
    
    try:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(__user_info__(user_id))
    except RuntimeError:
        # If no event loop is running, create a new one
        return asyncio.run(__user_info__(user_id))


# Command Handlers - PTB v22 Compatible
BL_HANDLER = CommandHandler("ignore", bl_user)
UNBL_HANDLER = CommandHandler("notice", unbl_user)
BLUSERS_HANDLER = CommandHandler("ignoredlist", bl_users)

# Add handlers to application
application.add_handler(BL_HANDLER)
application.add_handler(UNBL_HANDLER)
application.add_handler(BLUSERS_HANDLER)

__mod_name__ = "Blacklisting Users"
__handlers__ = [BL_HANDLER, UNBL_HANDLER, BLUSERS_HANDLER]

