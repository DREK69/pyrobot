from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup 

import MerissaRobot.Database.sql.chatbot_sql as sql
from MerissaRobot import pbot


def merissarm(update: Update, context: CallbackContext) -> str:
    query: Optional[CallbackQuery] = update.callback_query
    user: Optional[User] = update.effective_user
    match = re.match(r"rm_chat\((.+?)\)", query.data)
    if match:
        user_id = match.group(1)
        chat: Optional[Chat] = update.effective_chat
        is_merissa = sql.rem_merissa(chat.id)
        if is_merissa:
            is_merissa = sql.rem_merissa(user_id)
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"Merissa Chatbot Disable\n"
                f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            )
        else:
            update.effective_message.edit_text(
                "Merissa Chatbot disable by {}.".format(
                    mention_html(user.id, user.first_name)
                ),
                parse_mode=ParseMode.HTML,
            )

    return ""


def merissaadd(update: Update, context: CallbackContext) -> str:
    query: Optional[CallbackQuery] = update.callback_query
    user: Optional[User] = update.effective_user
    match = re.match(r"add_chat\((.+?)\)", query.data)
    if match:
        user_id = match.group(1)
        chat: Optional[Chat] = update.effective_chat
        is_merissa = sql.set_merissa(chat.id)
        if is_merissa:
            is_merissa = sql.set_merissa(user_id)
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"Merissa Chatbot Enable\n"
                f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            )
        else:
            update.effective_message.edit_text(
                "Merissa Chatbot enable by {}.".format(
                    mention_html(user.id, user.first_name)
                ),
                parse_mode=ParseMode.HTML,
            )

    return ""

@pbot.on_message(filters.command("chatbot"))
async def merissa(_, message):
    chatid = message.chat.id
    msg = """**Welcome To Control Panal Of Merissa ChatBot**

**Here You Will Find Two Buttons Select AnyOne Of Them**"""
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="On", callback_data=f"merissa add|{chatid}"),
                InlineKeyboardButton(text="Off", callback_data=f"merissa rm|{chatid}"),
            ]
        ]
    )
    await message.reply_text(
        msg,
        reply_markup=keyboard,
        parse_mode=ParseMode.MARKDOWN,
    )


def merissa_message(context: CallbackContext, message):
    reply_message = message.reply_to_message
    if message.text.lower() == "merissa":
        return True
    if reply_message:
        if reply_message.from_user.id == context.bot.get_me().id:
            return True
    else:
        return False


def chatbot(update: Update, context: CallbackContext):
    message = update.effective_message
    chat_id = update.effective_chat.id
    bot = context.bot
    is_merissa = sql.is_merissa(chat_id)
    if not is_merissa:
        return
    if message.text and not message.document:
        if not merissa_message(context, message):
            return
        bot.send_chat_action(chat_id, action="typing")
        results = requests.get(
            f"https://chat.merissabot.me/api/apikey=2030709195-MERISSAWk8XcW9hM3/message={message.text}"
        ).json()
        message.reply_text(results["reply"])


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
❂ `/ask question` : To get answer from Chatgpt By OpenAI.
❂ `/bard question` : To get answer from BardAI By Google.
"""

CHATBOTK_HANDLER = CommandHandler("chatbot", merissa)
ADD_CHAT_HANDLER = CallbackQueryHandler(merissaadd, pattern=r"add_chat")
RM_CHAT_HANDLER = CallbackQueryHandler(merissarm, pattern=r"rm_chat")
CHATBOT_HANDLER = MessageHandler(
    Filters.text
    & (~Filters.regex(r"^#[^\s]+") & ~Filters.regex(r"^!") & ~Filters.regex(r"^\/")),
    chatbot,
)
LIST_ALL_CHATS_HANDLER = CommandHandler(
    "allchats", list_all_chats, filters=CustomFilters.dev_filter
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
