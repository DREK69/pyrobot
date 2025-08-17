import html
import re

from telegram import Update
from telegram.ext import ContextTypes
from telegram.helpers import mention_html

from MerissaRobot.Handler.ptb.chat_status import cuser_admin
from MerissaRobot.Handler.ptb.decorators import merissacallback
from MerissaRobot.Modules.log_channel import loggable


@merissacallback(pattern=r"req_approve=")
@cuser_admin
@loggable
async def approve_joinReq(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    bot = context.bot
    query = update.callback_query
    user = update.effective_user
    chat = update.effective_chat
    match = re.match(r"req_approve=(.+)", query.data)

    user_id = match.group(1)
    try:
        await bot.approve_chat_join_request(chat.id, user_id)
        joined_user = await bot.get_chat_member(chat.id, user_id)
        joined_mention = mention_html(user_id, html.escape(joined_user.user.first_name))
        admin_mention = mention_html(user.id, html.escape(user.first_name))
        
        await update.effective_message.edit_text(
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
        await update.effective_message.edit_text(str(e))
        return ""


@merissacallback(pattern=r"req_decline=")
@cuser_admin
@loggable
async def decline_joinReq(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    bot = context.bot
    query = update.callback_query
    user = update.effective_user
    chat = update.effective_chat
    match = re.match(r"req_decline=(.+)", query.data)

    user_id = match.group(1)
    try:
        await bot.decline_chat_join_request(chat.id, user_id)
        joined_user = await bot.get_chat_member(chat.id, user_id)
        joined_mention = mention_html(user_id, html.escape(joined_user.user.first_name))
        admin_mention = mention_html(user.id, html.escape(user.first_name))
        
        await update.effective_message.edit_text(
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
        await update.effective_message.edit_text(str(e))
        return ""
