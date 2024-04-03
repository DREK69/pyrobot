import html
import re

from telegram.ext.callbackcontext import CallbackContext
from telegram.update import Update
from telegram.utils.helpers import mention_html

from MerissaRobot.Handler.ptb.chat_status import cuser_admin
from MerissaRobot.Handler.ptb.decorators import merissacallback
from MerissaRobot.Modules.log_channel import loggable


@merissacallback(pattern=r"req_approve=")
@cuser_admin
@loggable
def approve_joinReq(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    query = update.callback_query
    user = update.effective_user
    chat = update.effective_chat
    match = re.match(r"req_approve=(.+)", query.data)

    user_id = match.group(1)
    try:
        bot.approve_chat_join_request(chat.id, user_id)
        joined_user = bot.get_chat_member(chat.id, user_id)
        joined_mention = mention_html(user_id, html.escape(joined_user.user.first_name))
        admin_mention = mention_html(user.id, html.escape(user.first_name))
        update.effective_message.edit_text(
            f"{joined_mention}'s join request was approved by {admin_mention}.",
            parse_mode="HTML",
        )
        logmsg = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#JOIN_REQUEST\n"
            f"Approved\n"
            f"<b>Admin:</b> {admin_mention}\n"
            f"<b>User:</b> {joined_mention}\n"
        )
        return logmsg
    except Exception as e:
        update.effective_message.edit_text(str(e))


@merissacallback(pattern=r"req_decline=")
@cuser_admin
@loggable
def decline_joinReq(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    query = update.callback_query
    user = update.effective_user
    chat = update.effective_chat
    match = re.match(r"req_decline=(.+)", query.data)

    user_id = match.group(1)
    try:
        bot.decline_chat_join_request(chat.id, user_id)
        joined_user = bot.get_chat_member(chat.id, user_id)
        joined_mention = mention_html(user_id, html.escape(joined_user.user.first_name))
        admin_mention = mention_html(user.id, html.escape(user.first_name))
        update.effective_message.edit_text(
            f"{joined_mention}'s join request was declined by {admin_mention}.",
            parse_mode="HTML",
        )
        logmsg = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#JOIN_REQUEST\n"
            f"Declined\n"
            f"<b>Admin:</b> {admin_mention}\n"
            f"<b>User:</b> {joined_mention}\n"
        )
        return logmsg
    except Exception as e:
        update.effective_message.edit_text(str(e))
