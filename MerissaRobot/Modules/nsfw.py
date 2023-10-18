import os
import html
import nekos
import requests
from PIL import Image
from telegram import ParseMode
from MerissaRobot import dispatcher, updater
import MerissaRobot.Database.sql.nsfw_sql as sql
from MerissaRobot.Modules.log_channel import gloggable
from telegram import Message, Chat, Update, Bot, MessageEntity
from telegram.error import BadRequest, RetryAfter, Unauthorized
from telegram.ext import CommandHandler, run_async, CallbackContext
from MerissaRobot.Handler.filters import CustomFilters
from MerissaRobot.Handler.chat_status import user_admin
from telegram.utils.helpers import mention_html, mention_markdown, escape_markdown

@user_admin
@gloggable
def add_nsfw(update: Update, context: CallbackContext):
    chat = update.effective_chat
    msg = update.effective_message
    user = update.effective_user #Remodified by @EverythingSuckz
    is_nsfw = sql.is_nsfw(chat.id)
    if not is_nsfw:
        sql.set_nsfw(chat.id)
        msg.reply_text("Activated NSFW Mode!")
        message = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"ACTIVATED_NSFW\n"
            f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        )
        return message
    else:
        msg.reply_text("NSFW Mode is already Activated for this chat!")
        return ""


@user_admin
@gloggable
def rem_nsfw(update: Update, context: CallbackContext):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    is_nsfw = sql.is_nsfw(chat.id)
    if not is_nsfw:
        msg.reply_text("NSFW Mode is already Deactivated")
        return ""
    else:
        sql.rem_nsfw(chat.id)
        msg.reply_text("Rolled Back to SFW Mode!")
        message = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"DEACTIVATED_NSFW\n"
            f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        )
        return message

ADD_NSFW_HANDLER = CommandHandler("addnsfw", add_nsfw, run_async=True)
REMOVE_NSFW_HANDLER = CommandHandler("rmnsfw", rem_nsfw, run_async=True)

dispatcher.add_handler(ADD_NSFW_HANDLER)
dispatcher.add_handler(REMOVE_NSFW_HANDLER)

__handlers__ = [
    ADD_NSFW_HANDLER,
    REMOVE_NSFW_HANDLER,
]
