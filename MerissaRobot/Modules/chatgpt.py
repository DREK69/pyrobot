import html
import re

import requests
from googletrans import Translator
from telegram import (
    CallbackQuery,
    Chat,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode,
    Update,
    User,
)
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
)
from telegram.utils.helpers import mention_html

import MerissaRobot.Database.sql.chatbot_sql as sql
from MerissaRobot import dispatcher
from MerissaRobot.Handler.chat_status import user_admin, user_admin_no_reply
from MerissaRobot.Modules.log_channel import gloggable

tr = Translator()


@user_admin_no_reply
@gloggable
def chatgptrm(update: Update, context: CallbackContext) -> str:
    query: Optional[CallbackQuery] = update.callback_query
    user: Optional[User] = update.effective_user
    match = re.match(r"rm_gpt\((.+?)\)", query.data)
    if match:
        user_id = match.group(1)
        chat: Optional[Chat] = update.effective_chat
        is_chatgpt = sql.rem_chatgpt(chat.id)
        if is_chatgpt:
            is_chatgpt = sql.rem_chatgpt(user_id)
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"ChatGPT Disable\n"
                f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            )
        else:
            update.effective_message.edit_text(
                "ChatGPT disable by {}.".format(mention_html(user.id, user.first_name)),
                parse_mode=ParseMode.HTML,
            )

    return ""


@user_admin_no_reply
@gloggable
def chatgptadd(update: Update, context: CallbackContext) -> str:
    query: Optional[CallbackQuery] = update.callback_query
    user: Optional[User] = update.effective_user
    match = re.match(r"add_gpt\((.+?)\)", query.data)
    if match:
        user_id = match.group(1)
        chat: Optional[Chat] = update.effective_chat
        is_chatgpt = sql.set_chatgpt(chat.id)
        if is_chatgpt:
            is_chatgpt = sql.set_chatgpt(user_id)
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"ChatGPT Enable\n"
                f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            )
        else:
            update.effective_message.edit_text(
                "ChatGPT enable by {}.".format(mention_html(user.id, user.first_name)),
                parse_mode=ParseMode.HTML,
            )

    return ""


@user_admin
@gloggable
def chatgptai(update: Update, context: CallbackContext):    
    message = update.effective_message
    msg = """**Welcome To Control Panal Of ChatGPT AI**

**Here You Will Find Two Buttons Select AnyOne Of Them**"""
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="On", callback_data="add_gpt({})"),
                InlineKeyboardButton(text="Off", callback_data="rm_gpt({})"),
            ]
        ]
    )
    message.reply_text(
        msg,
        reply_markup=keyboard,
        parse_mode=ParseMode.MARKDOWN,
    )


def merissa_message(context: CallbackContext, message):
    reply_message = message.reply_to_message
    if message.text.lower() == "chatgpt":
        return True
    if reply_message:
        if reply_message.from_user.id == context.bot.get_me().id:
            return True
    else:
        return False


def chatgpt(update: Update, context: CallbackContext):
    message = update.effective_message
    chat_id = update.effective_chat.id
    bot = context.bot
    is_chatgpt = sql.is_chatgpt(chat_id)
    if not is_chatgpt:
        return
    if message.text and not message.document:
        if not merissa_message(context, message):
            return
        bot.send_chat_action(chat_id, action="typing")
        url = f"https://api.princexd.tech/chatgpt?ask={message.text}"
        results = requests.get(url).json()
        message.reply_text(results["answer"])


CHATGPT_HANDLER = CommandHandler("chatgpt", chatgptai)
ADD_CHATGPT_HANDLER = CallbackQueryHandler(chatgptadd, pattern=r"add_gpt")
RM_CHATGPT_HANDLER = CallbackQueryHandler(chatgptrm, pattern=r"rm_gpt")
CHATBOTGPT_HANDLER = MessageHandler(
    Filters.text
    & (~Filters.regex(r"^#[^\s]+") & ~Filters.regex(r"^!") & ~Filters.regex(r"^\/")),
    chatgpt,
)

dispatcher.add_handler(ADD_CHATGPT_HANDLER)
dispatcher.add_handler(CHATGPT_HANDLER)
dispatcher.add_handler(RM_CHATGPT_HANDLER)
dispatcher.add_handler(CHATBOTGPT_HANDLER)

__handlers__ = [
    ADD_CHATGPT_HANDLER,
    CHATGPT_HANDLER,
    RM_CHATGPT_HANDLER,
    CHATBOTGPT_HANDLER,
]
