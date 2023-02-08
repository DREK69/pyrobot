import itertools
from collections.abc import Iterable
from typing import Generator, List, Union

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler

import MerissaRobot.Database.sql.language_sql as sql
from MerissaRobot import dispatcher
from MerissaRobot.Handler.chat_status import user_admin, user_admin_no_reply
from MerissaRobot.Language import get_language, get_string


def paginate(iterable: Iterable, page_size: int) -> Generator[List, None, None]:
    while True:
        i1, i2 = itertools.tee(iterable)
        iterable, page = (
            itertools.islice(i1, page_size, None),
            list(itertools.islice(i2, page_size)),
        )
        if not page:
            break
        yield page


def gs(chat_id: Union[int, str], string: str) -> str:
    lang = sql.get_chat_lang(chat_id)
    return get_string(lang, string)


@user_admin
def set_lang(update: Update, _) -> None:
    chat = update.effective_chat
    msg = update.effective_message

    msg_text = gs(chat.id, "curr_chat_lang").format(
        get_language(sql.get_chat_lang(chat.id))[:-3]
    )

    msg.reply_text(
        msg_text,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="English 🇬🇧", callback_data="lang_en"),
                    InlineKeyboardButton(text="हिन्दी 🇮🇳", callback_data="lang_hi"),
                ],
                [
                    InlineKeyboardButton(text="ગુજરાતી 🇮🇳", callback_data="lang_gu"),
                    InlineKeyboardButton(text="తెలుగు 🇮🇳", callback_data="lang_te"),
                ],
                [
                    InlineKeyboardButton(text="Tamil 🇮🇳", callback_data="lang_ta"),
                    InlineKeyboardButton(text="Cheems 🐶", callback_data="lang_ch"),
                ],
                [
                    InlineKeyboardButton(
                        text="🌎 Help us with translation",
                        url=f"https://t.me/MerissaxSupport",
                    )
                ],
                [
                    InlineKeyboardButton(text="Close 🗑", callback_data="cb_close"),
                ],
            ]
        ),
    )


@user_admin_no_reply
def lang_button(update: Update, _) -> None:
    query = update.callback_query
    chat = update.effective_chat
    update.effective_message

    query.answer()
    lang = query.data.split("_")[1]
    sql.set_lang(chat.id, lang)
    msg_text = gs(chat.id, "set_chat_lang").format(get_language(lang)[:-3])
    AUTHOR = gs(chat.id, "authors")
    query.message.edit_text(
        msg_text,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="Author", url=f"https://t.me/{AUTHOR}"),
                    InlineKeyboardButton(text="Close 🗑", callback_data="cb_close"),
                ]
            ]
        ),
    )


def lang_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    chat = update.effective_chat
    update.effective_message

    msg_text = gs(chat.id, "curr_chat_lang").format(
        get_language(sql.get_chat_lang(chat.id))[:-3]
    )

    query.message.edit_text(
        msg_text,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="English 🇬🇧", callback_data="lang_en"),
                    InlineKeyboardButton(text="हिन्दी 🇮🇳", callback_data="lang_hi"),
                ],
                [
                    InlineKeyboardButton(text="ગુજરાતી 🇮🇳", callback_data="lang_gu"),
                    InlineKeyboardButton(text="తెలుగు 🇮🇳", callback_data="lang_te"),
                ],
                [
                    InlineKeyboardButton(text="Tamil 🇮🇳", callback_data="lang_ta"),
                    InlineKeyboardButton(text="Cheems 🐶", callback_data="lang_ch"),
                ],
                [
                    InlineKeyboardButton(
                        text="🌎 Help us with translation",
                        url=f"https://t.me/MerissaxSupport",
                    )
                ],
                [
                    InlineKeyboardButton(text="🔙 Back", callback_data="merissa_back"),
                    InlineKeyboardButton(text="Close 🗑", callback_data="cb_close"),
                ],
            ]
        ),
    )


def glang_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    chat = update.effective_chat
    update.effective_message

    msg_text = gs(chat.id, "curr_chat_lang").format(
        get_language(sql.get_chat_lang(chat.id))[:-3]
    )

    query.message.edit_text(
        msg_text,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="English 🇬🇧", callback_data="lang_en"),
                    InlineKeyboardButton(text="हिन्दी 🇮🇳", callback_data="lang_hi"),
                ],
                [
                    InlineKeyboardButton(text="ગુજરાતી 🇮🇳", callback_data="lang_gu"),
                    InlineKeyboardButton(text="తెలుగు 🇮🇳", callback_data="lang_te"),
                ],
                [
                    InlineKeyboardButton(text="Tamil 🇮🇳", callback_data="lang_ta"),
                    InlineKeyboardButton(text="Cheems 🐶", callback_data="lang_ch"),
                ],
                [
                    InlineKeyboardButton(
                        text="🌎 Help us with translation",
                        url=f"https://t.me/MerissaxSupport",
                    )
                ],
                [
                    InlineKeyboardButton(text="Close 🗑", callback_data="cb_close"),
                ],
            ]
        ),
    )


def font_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    update.effective_chat
    update.effective_message

    query.message.edit_text(
        text="Hey Dear, You Can Change Font Here Choose Fonts Using Below Button",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="🔠 Simple", callback_data="lang_cs"),
                    InlineKeyboardButton(text="🆒 Font", callback_data="lang_cf"),
                ],
                [   InlineKeyboardButton(text="Sᴍᴀʟʟ Cᴀᴘs", callback_data="lang_sc")],
                [
                    InlineKeyboardButton(text="🔙 Back", callback_data="merissa_back"),
                    InlineKeyboardButton(text="Close 🗑", callback_data="cb_close"),
                ],
            ]
        ),
    )


SETLANG_HANDLER = CommandHandler("setlang", set_lang)
SETLANG_BUTTON_HANDLER = CallbackQueryHandler(lang_button, pattern=r"lang_")
LANGUAGE_HANDLER = CallbackQueryHandler(
    lang_callback, pattern=r"cblang", run_async=True
)
GLANGUAGE_HANDLER = CallbackQueryHandler(
    glang_callback, pattern=r"cbglang", run_async=True
)
FONT_HANDLER = CallbackQueryHandler(font_callback, pattern=r"chfont", run_async=True)
dispatcher.add_handler(SETLANG_HANDLER)
dispatcher.add_handler(SETLANG_BUTTON_HANDLER)
dispatcher.add_handler(LANGUAGE_HANDLER)
dispatcher.add_handler(GLANGUAGE_HANDLER)
dispatcher.add_handler(FONT_HANDLER)
