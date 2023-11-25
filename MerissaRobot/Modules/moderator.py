import html

from telegram import ParseMode
from telegram.error import BadRequest
from telegram.utils.helpers import mention_html

import MerissaRobot.Database.sql.mod_sql as sql
from MerissaRobot import dispatcher
from MerissaRobot.Handler.ptb.chat_status import user_admin
from MerissaRobot.Handler.ptb.extraction import extract_user
from MerissaRobot.Modules.disable import DisableAbleCommandHandler.ptb
from MerissaRobot.Modules.log_channel import loggable


@loggable
@user_admin
def mod(update, context):
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    args = context.args
    user = update.effective_user
    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text(
            "I don't know who you're talking about, you're going to need to specify a user!"
        )
        return ""
    try:
        member = chat.get_member(user_id)
    except BadRequest:
        return ""
    if member.status == "administrator" or member.status == "creator":
        message.reply_text("No need to Modertor an Admin!")
        return ""
    if sql.is_modd(message.chat_id, user_id):
        message.reply_text(
            f"[{member.user['first_name']}](tg://user?id={member.user['id']}) is already moderator in {chat_title}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return ""
    sql.mod(message.chat_id, user_id)
    message.reply_text(
        f"[{member.user['first_name']}](tg://user?id={member.user['id']}) has been moderator in {chat_title}",
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
def dismod(update, context):
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    args = context.args
    user = update.effective_user
    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text(
            "I don't know who you're talking about, you're going to need to specify a user!"
        )
        return ""
    try:
        member = chat.get_member(user_id)
    except BadRequest:
        return ""
    if member.status == "administrator" or member.status == "creator":
        message.reply_text("This Is User Admin")
        return ""
    if not sql.is_modd(message.chat_id, user_id):
        message.reply_text(f"{member.user['first_name']} isn't moderator yet!")
        return ""
    sql.dismod(message.chat_id, user_id)
    message.reply_text(
        f"{member.user['first_name']} is no longer moderator in {chat_title}."
    )
    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#UNMODERTOR\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}"
    )

    return log_message


@user_admin
def modd(update, context):
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    msg = "The following users are Moderator.\n"
    modd_users = sql.list_modd(message.chat_id)
    for i in modd_users:
        member = chat.get_member(int(i.user_id))
        msg += f"{member.user['first_name']}\n"
    if msg.endswith("moderator.\n"):
        message.reply_text(f"No users are Moderator in {chat_title}.")
        return ""
    else:
        message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)


def modr(update, context):
    message = update.effective_message
    chat = update.effective_chat
    args = context.args
    user_id = extract_user(message, args)
    member = chat.get_member(int(user_id))
    if not user_id:
        message.reply_text(
            "I don't know who you're talking about, you're going to need to specify a user!"
        )
        return ""
    if sql.is_modd(message.chat_id, user_id):
        message.reply_text(f"{member.user['first_name']} is an moderator user.")
    else:
        message.reply_text(f"{member.user['first_name']} is not an moderator user.")


__help__ = """
❂ `/addmod`*:* moderator of a user. 
❂ `/rmmod`*:* Unmoderator of a user.
❂ `/modcheck`*:* moderation cheak of a user.
❂ `/modlist`*:* moderation user list.
"""

ADDMOD = DisableAbleCommandHandler.ptb("addmod", mod, run_async=True)
RMMOD = DisableAbleCommandHandler.ptb("rmmod", dismod, run_async=True)
MODLIST = DisableAbleCommandHandler.ptb("modlist", modd, run_async=True)
MODCHECK = DisableAbleCommandHandler.ptb("modcheck", modr, run_async=True)
dispatcher.add_handler(ADDMOD)
dispatcher.add_handler(RMMOD)
dispatcher.add_handler(MODLIST)
dispatcher.add_handler(MODCHECK)

__mod_name__ = "Moderation 👩‍✈️"
__command_list__ = ["addmod", "rmmod", "modlist", "modcheck"]
__handlers__ = [ADDMOD, RMMOD, MODLIST, MODCHECK]
