import html
import importlib
import json
import re
import time
import traceback
from sys import argv

import requests
from pyromod import listen  # ignore
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.error import (
    BadRequest,
    ChatMigrated,
    NetworkError,
    TelegramError,
    TimedOut,
    Unauthorized,
)
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
)
from telegram.ext.dispatcher import DispatcherHandlerStop
from telegram.utils.helpers import escape_markdown
from telethon.errors.rpcerrorlist import FloodWaitError

import MerissaRobot.Database.sql.users_sql as sql
from MerissaRobot import (
    LOGGER,
    OWNER_ID,
    SUPPORT_CHAT,
    TOKEN,
    dispatcher,
    pbot,
    telethn,
    updater,
)
from MerissaRobot.Handler.chat_status import is_user_admin
from MerissaRobot.Handler.misc import gpaginate_modules, paginate_modules
from MerissaRobot.Modules import ALL_MODULES
from MerissaRobot.text import (
    GROUP_HELP_BUTTON,
    GROUP_START_BUTTON,
    GROUP_START_TEXT,
    HELP_MODULE_TEXT,
    HELP_STRINGS,
    MERISSA_UPDATE_TEXT,
    PM_ABOUT_BUTTON,
    PM_ABOUT_TEXT,
    PM_DONATE_TEXT,
    PM_START_BUTTON,
    PM_START_TEXT,
    PM_SUPPORT_BUTTON,
    PM_SUPPORT_TEXT,
)

# needed to dynamically load Modules
# NOTE: Module order is not guaranteed, specify that in the config file!


def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time


IMPORTED = {}
MIGRATEABLE = []
HELPABLE = {}
STATS = []
USER_INFO = []
DATA_IMPORT = []
DATA_EXPORT = []
CHAT_SETTINGS = {}
USER_SETTINGS = {}

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("MerissaRobot.Modules." + module_name)
    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__

    if imported_module.__mod_name__.lower() not in IMPORTED:
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module
    else:
        raise Exception("Can't have two Modules with the same name! Please change one")

    if hasattr(imported_module, "__help__") and imported_module.__help__:
        HELPABLE[imported_module.__mod_name__.lower()] = imported_module

    # Chats to migrate on chat_migrated events
    if hasattr(imported_module, "__migrate__"):
        MIGRATEABLE.append(imported_module)

    if hasattr(imported_module, "__stats__"):
        STATS.append(imported_module)

    if hasattr(imported_module, "__user_info__"):
        USER_INFO.append(imported_module)

    if hasattr(imported_module, "__import_data__"):
        DATA_IMPORT.append(imported_module)

    if hasattr(imported_module, "__export_data__"):
        DATA_EXPORT.append(imported_module)

    if hasattr(imported_module, "__chat_settings__"):
        CHAT_SETTINGS[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "__user_settings__"):
        USER_SETTINGS[imported_module.__mod_name__.lower()] = imported_module


# do not async
def send_help(chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    dispatcher.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        reply_markup=keyboard,
    )


def convertmin(duration):
    seconds = int(duration)
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    result = f"{minutes}:{remaining_seconds}"
    return result


def test(update: Update, context: CallbackContext):
    # pprint(eval(str(update)))
    # update.effective_message.reply_text("Hola tester! _I_ *have* `markdown`", parse_mode=ParseMode.MARKDOWN)
    update.effective_message.reply_text("This person edited a message")
    print(update.effective_message)


def start(update: Update, context: CallbackContext):
    args = context.args
    chat = update.effective_chat
    update.effective_message
    if update.effective_chat.type == "private":
        if len(args) >= 1:
            if args[0].lower() == "help":
                send_help(update.effective_chat.id, HELP_STRINGS)
            elif args[0].lower().startswith("help_"):
                mod = args[0].lower().split("_", 1)[1]
                if not HELPABLE[imported_module.__mod_name__.lower().split(" ")[0]].get(
                    mod, False
                ):
                    return
                send_help(
                    update.effective_chat.id,
                    HELPABLE[mod].__help__,
                    InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="🔙 Back",
                                    callback_data="help_back",
                                )
                            ]
                        ]
                    ),
                )
            elif args[0].startswith("ytdl_"):
                videoid = args[0].split("ytdl_")[1]
                link = f"https://m.youtube.com/watch?v={videoid}"
                yt = requests.get(
                    f"https://api.princexd.tech/ytinfo?link={link}"
                ).json()
                videoid = yt["id"]
                thumbnail = requests.get(
                    f"https://api.princexd.tech/ytthumb?videoid={videoid}"
                ).json()["url"]
                title = yt["title"]
                duration = yt["duration"]
                dur = convertmin(duration)
                update.effective_message.reply_photo(
                    thumbnail,
                    caption=f"Title: {title}\nDuration: {dur}\n\nSelect Your Preferred Format from Below:",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "🔊 Audio",
                                    callback_data=f"audio {videoid}",
                                ),
                                InlineKeyboardButton(
                                    "🎥 Video", callback_data=f"formats {videoid}"
                                ),
                            ],
                            [
                                InlineKeyboardButton(
                                    "🗑️ Close", callback_data="cb_close"
                                ),
                            ],
                        ]
                    ),
                )
            elif args[0].lower().startswith("stngs_"):
                match = re.match("stngs_(.*)", args[0].lower())
                chat = dispatcher.bot.getChat(match.group(1))

                if is_user_admin(chat, update.effective_user.id):
                    send_settings(match.group(1), update.effective_user.id, False)
                else:
                    send_settings(match.group(1), update.effective_user.id, True)

            elif args[0][1:].isdigit() and "rules" in IMPORTED:
                IMPORTED["rules"].send_rules(update, args[0], from_pm=True)
        else:
            update.effective_message.reply_text(
                text=PM_START_TEXT,
                reply_markup=PM_START_BUTTON,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=False,
            )
    else:
        update.effective_message.reply_text(
            text=GROUP_START_TEXT,
            parse_mode=ParseMode.HTML,
            reply_markup=GROUP_START_BUTTON,
        )


def error_handler(update, context):
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    LOGGER.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    message = (
        "An exception was raised while handling an update\n"
        "<pre>update = {}</pre>\n\n"
        "<pre>{}</pre>"
    ).format(
        html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False)),
        html.escape(tb),
    )

    if len(message) >= 4096:
        message = message[:4096]
    # Finally, send the message
    context.bot.send_message(chat_id=OWNER_ID, text=message, parse_mode=ParseMode.HTML)


# for test purposes
def error_callback(update: Update, context: CallbackContext):
    error = context.error
    try:
        raise error
    except Unauthorized:
        print("no nono1")
        print(error)
        # remove update.message.chat_id from conversation list
    except BadRequest:
        print("no nono2")
        print("BadRequest caught")
        print(error)

        # handle malformed requests - read more below!
    except TimedOut:
        print("no nono3")
        # handle slow connection problems
    except NetworkError:
        print("no nono4")
        # handle other connection problems
    except ChatMigrated as err:
        print("no nono5")
        print(err)
        # the chat_id of a group has changed, use e.new_chat_id instead
    except TelegramError:
        print(error)
        # handle all other telegram related errors


def help_button(update, context):
    update.effective_chat
    query = update.callback_query
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)

    print(query.message.chat.id)

    try:
        if mod_match:
            module = mod_match.group(1)
            text = (
                HELP_MODULE_TEXT.format(HELPABLE[module].__mod_name__)
                + HELPABLE[module].__help__
            )
            if hasattr(HELPABLE[module], "__helpbtns__"):
                button = HELPABLE[module].__helpbtns__
            if not hasattr(HELPABLE[module], "__helpbtns__"):
                button = [[InlineKeyboardButton("🔙 Back", callback_data="help_back")]]
            query.message.edit_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(button),
            )

        elif prev_match:
            curr_page = int(prev_match.group(1))
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(curr_page - 1, HELPABLE, "help")
                ),
            )

        elif next_match:
            next_page = int(next_match.group(1))
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(next_page + 1, HELPABLE, "help")
                ),
            )

        elif back_match:
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, HELPABLE, "help")
                ),
            )

        # ensure no spinny white circle
        context.bot.answer_callback_query(query.id)
    except BadRequest:
        pass


def ghelp_button(update, context):
    update.effective_chat
    query = update.callback_query
    mod_match = re.match(r"ghelp_module\((.+?)\)", query.data)
    prev_match = re.match(r"ghelp_prev\((.+?)\)", query.data)
    next_match = re.match(r"ghelp_next\((.+?)\)", query.data)
    back_match = re.match(r"ghelp_back", query.data)

    print(query.message.chat.id)

    try:
        if mod_match:
            module = mod_match.group(1)
            text = (
                HELP_MODULE_TEXT.format(HELPABLE[module].__mod_name__)
                + HELPABLE[module].__help__
            )
            if hasattr(HELPABLE[module], "__helpbtns__"):
                button = HELPABLE[module].__helpbtns__
            if not hasattr(HELPABLE[module], "__helpbtns__"):
                button = [[InlineKeyboardButton("🔙 Back", callback_data="ghelp_back")]]
            query.message.edit_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(button),
            )

        elif prev_match:
            curr_page = int(prev_match.group(1))
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    gpaginate_modules(curr_page - 1, HELPABLE, "ghelp")
                ),
            )

        elif next_match:
            next_page = int(next_match.group(1))
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    gpaginate_modules(next_page + 1, HELPABLE, "ghelp")
                ),
            )

        elif back_match:
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    gpaginate_modules(0, HELPABLE, "ghelp")
                ),
            )

        # ensure no spinny white circle
        context.bot.answer_callback_query(query.id)
    except BadRequest:
        pass


def merissa_about_callback(update, context):
    update.effective_chat
    query = update.callback_query
    if query.data == "merissa_":
        query.message.edit_text(
            text=HELP_STRINGS,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=PM_ABOUT_BUTTON,
        )
    elif query.data == "merissa_back":
        query.message.edit_text(
            text=PM_START_TEXT,
            reply_markup=PM_START_BUTTON,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )
    elif query.data == "merissa_about":
        query.message.edit_text(
            text=PM_ABOUT_TEXT,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="🔙 Back", callback_data="merissa_")]]
            ),
        )

    elif query.data == "merissa_source":
        query.message.reply_sticker(
            "CAACAgUAAxkBAAJRAWLx-zmJ62FNVR9gnl4w22X5qRlqAAKyBAADwEBWQxLxqPtRziMpBA"
        )
        query.message.delete()

    elif query.data == "merissa_latestup":
        query.message.edit_text(
            MERISSA_UPDATE_TEXT,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="🔙 Back", callback_data="merissa_back"
                        ),
                        InlineKeyboardButton(
                            text="Previous ▶️", callback_data="merissa_upv2"
                        ),
                    ]
                ]
            ),
        )
    elif query.data == "merissa_upv1":
        query.message.edit_text(
            """──「 Merissa v1.0 Update 」──

- Added Anti-Language, Anti-Spam, Anti-Channel, Anti-Services
- Added Tagalert, Tagall, Chatbot, UrlLock, Captcha, GenQR
- Update Help Menu Bar""",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="🔙 Back", callback_data="merissa_upv2")]]
            ),
        )
    elif query.data == "merissa_upv2":
        query.message.edit_text(
            text="""──「 Merissa v2.0 Update 」──

- Added Anti-Raid, Games, Animations, Attendance, Whisper, Rename, SessionHack, Insta, Tiktok and Movie Downloader, Mod Apk Downloader.
- Update Chatbot, Quotly, Federation Like Rose Bot, Captcha
- Update Afk Added Gif
- Multi Language Bot""",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="🔙 Back", callback_data="merissa_latestup"
                        ),
                        InlineKeyboardButton(
                            text="Previous ▶️", callback_data="merissa_upv1"
                        ),
                    ]
                ]
            ),
        )
    elif query.data == "merissa_support":
        query.message.edit_text(
            text=PM_SUPPORT_TEXT,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=PM_SUPPORT_BUTTON,
        )
    elif query.data == "merissa_setting":
        query.message.edit_text(
            text="Choose where you want help section using below Button",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=GROUP_HELP_BUTTON,
        )
    elif query.data == "merissa_private":
        userid = query.from_user.id
        query.answer("Help Menu Sent in Private Chat", show_alert=True)
        send_help(
            userid,
            text=HELP_STRINGS,
        )

    elif query.data == "merissa_donate":
        query.message.edit_text(
            text=PM_DONATE_TEXT,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="🔙 Back", callback_data="merissa_"),
                    ]
                ]
            ),
        )


def Source_about_callback(update, context):
    query = update.callback_query
    if query.data == "source_":
        query.message.edit_text(
            text="๏›› This advance command for Musicplayer."
            "\n\n๏ Command for admins only."
            "\n • `/reload` - For refreshing the adminlist."
            "\n • `/pause` - To pause the playback."
            "\n • `/resume` - To resuming the playback You've paused."
            "\n • `/skip` - To skipping the player."
            "\n • `/end` - For end the playback."
            "\n • `/musicplayer <on/off>` - Toggle for turn ON or turn OFF the musicplayer."
            "\n\n๏ Command for all members."
            "\n • `/play` <query /reply audio> - Playing music via YouTube."
            "\n • `/playlist` - To playing a playlist of groups or your personal playlist",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="Go Back", callback_data="merissa_")]]
            ),
        )
    elif query.data == "source_back":
        first_name = update.effective_user.first_name
        query.message.edit_text(
            PM_START_TEXT.format(
                escape_markdown(first_name),
                escape_markdown(uptime),
                sql.num_users(),
                sql.num_chats(),
            ),
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN,
            timeout=60,
            disable_web_page_preview=False,
        )


def get_help(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    args = update.effective_message.text.split(None, 1)

    # ONLY send help in PM
    if chat.type != chat.PRIVATE:
        if len(args) >= 2 and any(args[1].lower().split(" ")[0] == x for x in HELPABLE):
            module = args[1].lower()
            update.effective_message.reply_text(
                f"Contact me in PM to get help of {module.capitalize()}",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Help ❓",
                                url="t.me/{}?start=help_{}".format(
                                    context.bot.username, module
                                ),
                            )
                        ]
                    ]
                ),
            )
            return
        update.effective_message.reply_text(
            text="Contact me in PM to get the list of possible commands.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="👤 Open in Private Chat",
                            callback_data=f"merissa_private",
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="👥 Open Here", callback_data="ghelp_back"
                        ),
                    ],
                ]
            ),
        )
        return

    elif len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
        module = args[1].lower()
        text = (
            "Here is the available help for the *{}* module:\n".format(
                HELPABLE[module].__mod_name__
            )
            + HELPABLE[module].__help__
        )
        send_help(
            chat.id,
            text,
            InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="🔙 Back", callback_data="help_back")]]
            ),
        )

    else:
        send_help(chat.id, HELP_STRINGS)


def send_settings(chat_id, user_id, user=False):
    if user:
        if USER_SETTINGS:
            settings = "\n\n".join(
                "*{}*:\n{}".format(mod.__mod_name__, mod.__user_settings__(user_id))
                for mod in USER_SETTINGS.values()
            )
            dispatcher.bot.send_message(
                user_id,
                text="Which module would you like to check {}'s settings for?"
                + "\n\n"
                + settings,
                parse_mode=ParseMode.MARKDOWN,
            )

        else:
            dispatcher.bot.send_message(
                user_id,
                "Seems like there aren't any user specific settings available :'(",
                parse_mode=ParseMode.MARKDOWN,
            )

    else:
        if CHAT_SETTINGS:
            chat_name = dispatcher.bot.getChat(chat_id).title
            dispatcher.bot.send_message(
                user_id,
                text=gs(chat_id, "pm_settings_group_text").format(chat_name),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )
        else:
            dispatcher.bot.send_message(
                user_id,
                "Seems like there aren't any chat settings available :'(\nSend this "
                "in a group chat you're admin in to find its current settings!",
                parse_mode=ParseMode.MARKDOWN,
            )


def settings_button(update: Update, context: CallbackContext):
    query = update.callback_query
    user = update.effective_user
    bot = context.bot
    chat = update.effective_chat
    mod_match = re.match(r"stngs_module\((.+?),(.+?)\)", query.data)
    prev_match = re.match(r"stngs_prev\((.+?),(.+?)\)", query.data)
    next_match = re.match(r"stngs_next\((.+?),(.+?)\)", query.data)
    back_match = re.match(r"stngs_back\((.+?)\)", query.data)
    try:
        if mod_match:
            chat_id = mod_match.group(1)
            module = mod_match.group(2)
            chat = bot.get_chat(chat_id)
            text = "*{}* has the following settings for the *{}* module:\n\n".format(
                escape_markdown(chat.title), CHAT_SETTINGS[module].__mod_name__
            ) + CHAT_SETTINGS[module].__chat_settings__(chat_id, user.id)
            query.message.reply_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Go Back",
                                callback_data="stngs_back({})".format(chat_id),
                            )
                        ]
                    ]
                ),
            )

        elif prev_match:
            chat_id = prev_match.group(1)
            curr_page = int(prev_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                text="Hi there! There are quite a few settings for {} - go ahead and pick what you're interested in.".format(
                    chat.title
                ),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        curr_page - 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif next_match:
            chat_id = next_match.group(1)
            next_page = int(next_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                text="Hi there! There are quite a few settings for {} - go ahead and pick what you're interested in.".format(
                    chat.title
                ),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        next_page + 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif back_match:
            chat_id = back_match.group(1)
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                text="Hi there! There are quite a few settings for {} - go ahead and pick what you're interested in.".format(
                    escape_markdown(chat.title)
                ),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )

        # ensure no spinny white circle
        bot.answer_callback_query(query.id)
        query.message.delete()
    except BadRequest as excp:
        if excp.message not in [
            "Message is not modified",
            "Query_id_invalid",
            "Message can't be deleted",
        ]:
            LOGGER.exception("Exception in settings buttons. %s", str(query.data))


def get_settings(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message  # type: Optional[Message]

    # ONLY send settings in PM
    if chat.type != chat.PRIVATE:
        if is_user_admin(chat, user.id):
            text = "Click here to get this chat's settings, as well as yours."
            msg.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Settings ⚙️",
                                url="t.me/{}?start=stngs_{}".format(
                                    context.bot.username, chat.id
                                ),
                            )
                        ]
                    ]
                ),
            )
        else:
            text = "Click here to check your settings."

    else:
        send_settings(chat.id, user.id, True)


def donate(update: Update, context: CallbackContext):
    update.effective_message.from_user
    chat = update.effective_chat  # type: Optional[Chat]
    context.bot
    update.effective_message.reply_text(
        text=PM_DONATE_TEXT,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
    )


def migrate_chats(update: Update, context: CallbackContext):
    msg = update.effective_message  # type: Optional[Message]
    if msg.migrate_to_chat_id:
        old_chat = update.effective_chat.id
        new_chat = msg.migrate_to_chat_id
    elif msg.migrate_from_chat_id:
        old_chat = msg.migrate_from_chat_id
        new_chat = update.effective_chat.id
    else:
        return

    LOGGER.info("Migrating from %s, to %s", str(old_chat), str(new_chat))
    for mod in MIGRATEABLE:
        mod.__migrate__(old_chat, new_chat)

    LOGGER.info("Successfully migrated!")
    raise DispatcherHandlerStop


def main():
    if SUPPORT_CHAT is not None and isinstance(SUPPORT_CHAT, str):
        try:
            dispatcher.bot.sendMessage(
                2030709195,
                "👋 Hi, I am Successfully Updated.",
                parse_mode=ParseMode.MARKDOWN,
            )
        except Unauthorized:
            LOGGER.warning(
                "Bot isnt able to send message to support_chat, go and check!"
            )
        except BadRequest as e:
            LOGGER.warning(e.message)

    test_handler = CommandHandler("test", test, run_async=True)
    start_handler = CommandHandler("start", start, run_async=True)

    help_handler = CommandHandler("help", get_help, run_async=True)
    help_callback_handler = CallbackQueryHandler(
        help_button, pattern=r"help_.*", run_async=True
    )

    ghelp_callback_handler = CallbackQueryHandler(
        ghelp_button, pattern=r"ghelp_.*", run_async=True
    )

    settings_handler = CommandHandler("settings", get_settings, run_async=True)
    settings_callback_handler = CallbackQueryHandler(
        settings_button, pattern=r"stngs_", run_async=True
    )

    about_callback_handler = CallbackQueryHandler(
        merissa_about_callback, pattern=r"merissa_", run_async=True
    )

    source_callback_handler = CallbackQueryHandler(
        Source_about_callback, pattern=r"source_", run_async=True
    )

    donate_handler = CommandHandler("donate", donate, run_async=True)
    migrate_handler = MessageHandler(
        Filters.status_update.migrate, migrate_chats, run_async=True
    )

    dispatcher.add_handler(test_handler)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(about_callback_handler)
    dispatcher.add_handler(source_callback_handler)
    dispatcher.add_handler(settings_handler)
    dispatcher.add_handler(help_callback_handler)
    dispatcher.add_handler(ghelp_callback_handler)
    dispatcher.add_handler(settings_callback_handler)
    dispatcher.add_handler(migrate_handler)
    dispatcher.add_handler(donate_handler)

    dispatcher.add_error_handler(error_callback)

    LOGGER.info("MerissaRobot Started Successfully")
    updater.start_polling(timeout=15, read_latency=4, drop_pending_updates=True)

    if len(argv) not in (1, 3, 4):
        telethn.disconnect()
    else:
        telethn.run_until_disconnected()

    updater.idle()


if __name__ == "__main__":
    LOGGER.info("Successfully loaded Modules: " + str(ALL_MODULES))
    pbot.start()
    try:
        telethn.start(bot_token=TOKEN)
    except FloodWaitError as e:
        LOGGER.info(
            f"[FloodWaitError] Have to wait {e.seconds} seconds due to FloodWait."
        )
        time.sleep(e.seconds)
        telethn.start(bot_token=TOKEN)
    main()
