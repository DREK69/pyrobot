import html

from telegram import Update
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.ext import ContextTypes
from telegram.helpers import mention_html

import MerissaRobot.Database.sql.mod_sql as sql
from MerissaRobot import application
from MerissaRobot.Handler.ptb.chat_status import user_admin
from MerissaRobot.Handler.ptb.extraction import extract_user
from MerissaRobot.Modules.disable import DisableAbleCommandHandler
from MerissaRobot.Modules.log_channel import loggable


@loggable
@user_admin
async def mod(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    args = context.args
    user = update.effective_user
    user_id = extract_user(message, args)
    if not user_id:
        await message.reply_text(
            "I don't know who you're talking about, you're going to need to specify a user!"
        )
        return ""
    try:
        member = await chat.get_member(user_id)
    except BadRequest:
        return ""
    if member.status == "administrator" or member.status == "creator":
        await message.reply_text("No need to Moderator an Admin!")
        return ""
    if sql.is_modd(message.chat_id, user_id):
        await message.reply_text(
            f"[{member.user.first_name}](tg://user?id={member.user.id}) is already moderator in {chat_title}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return ""
    sql.mod(message.chat_id, user_id)
    await message.reply_text(
        f"[{member.user.first_name}](tg://user?id={member.user.id}) has been moderator in {chat_title}",
        parse_mode=ParseMode.MARKDOWN,
    )
    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#MODERATOR\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}"
    )

    return log_message


@loggable
@user_admin
async def dismod(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    args = context.args
    user = update.effective_user
    user_id = extract_user(message, args)
    if not user_id:
        await message.reply_text(
            "I don't know who you're talking about, you're going to need to specify a user!"
        )
        return ""
    try:
        member = await chat.get_member(user_id)
    except BadRequest:
        return ""
    if member.status == "administrator" or member.status == "creator":
        await message.reply_text("This Is User Admin")
        return ""
    if not sql.is_modd(message.chat_id, user_id):
        await message.reply_text(f"{member.user.first_name} isn't moderator yet!")
        return ""
    sql.dismod(message.chat_id, user_id)
    await message.reply_text(
        f"{member.user.first_name} is no longer moderator in {chat_title}."
    )
    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#UNMODERTOR\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}"
    )

    return log_message


@user_admin
async def modd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    msg = "The following users are Moderator.\n"
    modd_users = sql.list_modd(message.chat_id)
    for i in modd_users:
        try:
            member = await chat.get_member(int(i.user_id))
            msg += f"{member.user.first_name}\n"
        except BadRequest:
            # Skip if user not found
            continue
    if msg.endswith("Moderator.\n"):
        await message.reply_text(f"No users are Moderator in {chat_title}.")
        return ""
    else:
        await message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)


async def modr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat = update.effective_chat
    args = context.args
    user_id = extract_user(message, args)
    if not user_id:
        await message.reply_text(
            "I don't know who you're talking about, you're going to need to specify a user!"
        )
        return ""
    try:
        member = await chat.get_member(int(user_id))
        if sql.is_modd(message.chat_id, user_id):
            await message.reply_text(f"{member.user.first_name} is an moderator user.")
        else:
            await message.reply_text(f"{member.user.first_name} is not an moderator user.")
    except BadRequest:
        await message.reply_text("User not found in this chat.")


__help__ = """
❂ `/addmod`*:* moderator of a user. 
❂ `/rmmod`*:* Unmoderator of a user.
❂ `/modcheck`*:* moderation check of a user.
❂ `/modlist`*:* moderation user list.
"""

ADDMOD = DisableAbleCommandHandler("addmod", mod, block=False)
RMMOD = DisableAbleCommandHandler("rmmod", dismod, block=False)
MODLIST = DisableAbleCommandHandler("modlist", modd, block=False)
MODCHECK = DisableAbleCommandHandler("modcheck", modr, block=False)

application.add_handler(ADDMOD)
application.add_handler(RMMOD)
application.add_handler(MODLIST)
application.add_handler(MODCHECK)

__mod_name__ = "Moderation 👩‍✈️"
__command_list__ = ["addmod", "rmmod", "modlist", "modcheck"]
__handlers__ = [ADDMOD, RMMOD, MODLIST, MODCHECK]
