import html
import json
import random
import re
from time import sleep

import openai
import requests
from telegram import (
    CallbackQuery,
    Chat,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode,
    Update,
    User,
)
from telegram.error import BadRequest, RetryAfter, Unauthorized
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
from MerissaRobot.Handlers.filters import CustomFilters
from MerissaRobot.Handlers.validation import user_admin, user_admin_no_reply
from MerissaRobot.Plugins.Admin.log_channel import gloggable


@user_admin_no_reply
@gloggable
def merissarm(update: Update, context: CallbackContext) -> str:
    query: Optional[CallbackQuery] = update.callback_query
    user: Optional[User] = update.effective_user
    match = re.match(r"rm_chat\((.+?)\)", query.data)
    if match:
        user_id = match.group(1)
        chat: Optional[Chat] = update.effective_chat
        try:
            is_merissa = sql.rem_merissa(chat.id)
        except Exception as e:
            update.effective_message.edit_text(f"error occured: {e}")
            return

        if is_merissa:
            is_merissa = sql.rem_merissa(user_id)
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"AI_DISABLED\n"
                f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            )
        else:
            update.effective_message.edit_text(
                "Chatbot disable by {}.".format(mention_html(user.id, user.first_name)),
                parse_mode=ParseMode.HTML,
            )

    return ""


@user_admin_no_reply
@gloggable
def merissaadd(update: Update, context: CallbackContext) -> str:
    query: Optional[CallbackQuery] = update.callback_query
    user: Optional[User] = update.effective_user
    match = re.match(r"add_chat\((.+?)\)", query.data)
    if match:
        user_id = match.group(1)
        chat: Optional[Chat] = update.effective_chat
        is_merissa = sql.set_merissa(chat.id)
        if is_merissa:
            try:
                is_merissa = sql.set_merissa(user_id)
            except Exception as e:
                update.effective_message.edit_text(f"error occured: {e}")
                return
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"AI_ENABLE\n"
                f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            )
        else:
            update.effective_message.edit_text(
                "Chatbot enable by {}.".format(mention_html(user.id, user.first_name)),
                parse_mode=ParseMode.HTML,
            )

    return ""


@user_admin
@gloggable
def merissa(update: Update, context: CallbackContext):
    update.effective_user
    message = update.effective_message
    msg = """**Welcome To Control Panal Of Merissa ChatBot**

**Here You Will Find Two Buttons Select AnyOne Of Them**"""
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="On", callback_data="add_chat({})"),
                InlineKeyboardButton(text="Off", callback_data="rm_chat({})"),
            ]
        ]
    )
    message.reply_text(
        msg,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
    )


def merissa_message(context: CallbackContext, message):
    reply_message = message.reply_to_message
    if message.text.lower() == "merissa":
        return True
    if message.chat.type == "private":
        return True

    if reply_message:
        if reply_message.from_user.id == context.bot.get_me().id:
            return True
    else:
        return False


# Define the rules for different types of messages
rules = {
    "greeting": [
        "hi",
        "hello",
        "hey",
        "good morning",
        "good afternoon",
        "good evening",
        "howdy",
    ],
    "compliment": [
        "beautiful",
        "nice",
        "lovely",
        "stunning",
        "gorgeous",
        "amazing",
        "wonderful",
    ],
    "flirtation": [
        "hug",
        "kiss",
        "date",
        "cuddle",
        "snuggle",
        "miss you",
        "you're so cute",
        "love",
    ],
    "joke": [
        "haha",
        "lol",
        "funny",
        "that's a good one",
        "you crack me up",
        "I can't stop laughing",
    ],
    "small talk": [
        "how are you",
        "what's up",
        "what's new",
        "how was your day",
        "what are you doing",
        "nice weather today",
    ],
    "timepass": ["okay", "cool", "nice", "alright", "got it", "thanks"],
    "unknown": [
        "I don't understand",
        "can you clarify",
        "what do you mean",
        "sorry, I don't know",
        "could you please rephrase that",
    ],
    "abuse": [
        "fuck",
        "motherfucker",
        "bitch",
        "pussy",
        "dick",
        "vagina",
        "motherchod",
        "gandu",
        "bhosdike",
        "chutiya",
        "loda",
        "bahanchod",
        "chut",
        "loda",
        "behanchod",
        "matherchod",
        "randi",
        "jhatu",
        "jhat",
        "lund",
        "lawde",
        "boobs",
    ],
}


def chatbot(update: Update, context: CallbackContext):
    message = update.effective_message
    chat_id = update.effective_chat.id
    bot = context.bot
    # Check if the chat has enabled the chatbot
    is_merissa_enabled = sql.is_merissa(chat_id)
    if not is_merissa_enabled:
        return
    # Set up OpenAI API key and models
    openai.api_key = "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"
    if message.text and not message.document:
        try:
            if not merissa_message(context, message):
                return
            bot.send_chat_action(chat_id, action="typing")

            message_text = message.text.strip().lower()

            # Set a threshold to detect timepass messages
            threshold = 30
            small_threshold = 10

            prompt = message_text
            temperature = random.uniform(0.5, 1.0)

            # Check if the message is a timepass or a serious question
            if len(message_text) <= threshold:
                is_timepass = any(word in message_text for word in rules["timepass"])
                if is_timepass:
                    # Use Kora API to generate response
                    merissaurl = requests.get(
                        "https://merissachatbot.vercel.app/chatbot/Merissa/Prince/message="
                        + message_text
                    )
                    merissa = json.loads(merissaurl.text)["reply"]
                else:
                    for rule, words in rules.items():
                        if any(word in message_text for word in words):
                            # Use Kora API to generate response for certain rules
                            merissaurl = requests.get(
                                "https://merissachatbot.vercel.app/chatbot/Merissa/Prince/message="
                                + message_text
                            )
                            merissa = json.loads(merissaurl.text)["reply"]
                            break
                    else:
                        if len(message_text) <= small_threshold:
                            merissa_url = f"https://merissachatbot.vercel.app/chatbot/Merissa/Prince/message={message_text}"
                            merissa = json.loads(requests.get(merissa_url).text)[
                                "reply"
                            ]
                        else:
                            # If none of the rules match, randomly choose between Kora and OpenAI API
                            if random.random() < 0.3:
                                merissa_url = f"https://merissachatbot.vercel.app/chatbot/Merissa/Prince/message={message_text}"
                                merissa = json.loads(requests.get(merissa_url).text)[
                                    "reply"
                                ]
                            else:
                                # Use OpenAI API to generate response for unknown intentions
                                response = openai.Completion.create(
                                    model="text-davinci-003",
                                    prompt=message_text,
                                    temperature=temperature,
                                    max_tokens=500,
                                    top_p=0,
                                    frequency_penalty=0,
                                    presence_penalty=0.6,
                                )
                                merissa = response.choices[0].text
            else:
                # Use OpenAI API to generate response for serious questions
                response = openai.Completion.create(
                    model="text-davinci-003",
                    prompt=prompt,
                    temperature=temperature,
                    max_tokens=500,
                    top_p=0,
                    frequency_penalty=0,
                    presence_penalty=0.6,
                )
                merissa = response.choices[0].text

            # Send the translated response to the user
            message.reply_text(merissa)

        except Exception as e:
            # Log the error and send a message to the user that there was a problem
            context.bot.send_message(
                chat_id=chat_id, text=f"Sorry, I encountered an error: {str(e)}"
            )


def list_all_chats(update: Update, context: CallbackContext):
    chats = sql.get_all_merissa_chats()
    text = "<b>Merissa-Enabled Chats</b>\n"
    for chat in chats:
        try:
            x = context.bot.get_chat(int(*chat))
            name = x.title or x.first_name
            text += f"• <code>{name}</code>\n"
        except (BadRequest, Unauthorized):
            sql.rem_merissa(*chat)
        except RetryAfter as e:
            sleep(e.retry_after)
    update.effective_message.reply_text(text, parse_mode="HTML")


__mod_name__ = "Chatbot 🤖"
__help__ = """
Merissa AI ChatBot is the only ai system which can detect & reply upto 200 language's

For Chatbot turn on/off:
❂ `/chatbot`: To On Or Off ChatBot In Your Chat.

For Merissa Chatbot Api:
❂ `/token` : To get your Merissa Chatbot Token.
❂ `/revoke` : To revoke/delete Merissa Chatbot Token.

For Asking Questions to ChatGPT:
❂ `/chatgpt` on/off : To on or off chatgpt chat.
❂ `/ask question` : To get answer from Chatgpt By OpenAI.

*Reports bugs at*: @MerissaxSupport
*Powered by* @MerissaRobot"""

__helpbtns__ = [
    [
        InlineKeyboardButton(
            "For Devlopers Merissa ChatApi", url="https://t.me/Merissachatbotapi"
        ),
    ],
    [InlineKeyboardButton("🔙 Back", callback_data="help_back")],
]


CHATBOTK_HANDLER = CommandHandler("chatbot", merissa, run_async=True)
ADD_CHAT_HANDLER = CallbackQueryHandler(merissaadd, pattern=r"add_chat", run_async=True)
RM_CHAT_HANDLER = CallbackQueryHandler(merissarm, pattern=r"rm_chat", run_async=True)
CHATBOT_HANDLER = MessageHandler(
    Filters.text
    & (~Filters.regex(r"^#[^\s]+") & ~Filters.regex(r"^!") & ~Filters.regex(r"^\/")),
    chatbot,
    run_async=True,
)
LIST_ALL_CHATS_HANDLER = CommandHandler(
    "allchats", list_all_chats, filters=CustomFilters.dev_filter, run_async=True
)

dispatcher.add_handler(ADD_CHAT_HANDLER)
dispatcher.add_handler(CHATBOTK_HANDLER)
dispatcher.add_handler(RM_CHAT_HANDLER)
dispatcher.add_handler(LIST_ALL_CHATS_HANDLER)
dispatcher.add_handler(CHATBOT_HANDLER)

__handlers__ = [
    ADD_CHAT_HANDLER,
    CHATBOTK_HANDLER,
    RM_CHAT_HANDLER,
    LIST_ALL_CHATS_HANDLER,
    CHATBOT_HANDLER,
]
