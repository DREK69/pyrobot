import asyncio
import html
import importlib
import json
import re
import time
import traceback

from pyrogram.errors.exceptions.flood_420 import FloodWait
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import (
    BadRequest,
    ChatMigrated,
    NetworkError,
    TelegramError,
    TimedOut,
)
from telegram.ext import (
    Application,
    ContextTypes,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)
from telegram.constants import ParseMode
from telegram.helpers import escape_markdown
from telethon.errors.rpcerrorlist import FloodWaitError

import MerissaRobot.Database.sql.users_sql as sql
from MerissaRobot import (
    LOGGER,
    OWNER_ID,
    TOKEN,
    application,  # Changed from dispatcher
    pbot,
    pytgcalls,
    telethn,
    user,
)
from MerissaRobot.Handler.ptb.chat_status import is_user_admin
from MerissaRobot.Handler.ptb.misc import gpaginate_modules, paginate_modules
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

# ───────────────────────────────
# Global Variables and Setup
# ───────────────────────────────
StartTime = time.time()

IMPORTED = {}
MIGRATEABLE = []
HELPABLE = {}
STATS = []
USER_INFO = []
DATA_IMPORT = []
DATA_EXPORT = []
CHAT_SETTINGS = {}
USER_SETTINGS = {}


# ───────────────────────────────
# Utility Functions
# ───────────────────────────────
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


def convertmin(duration):
    seconds = int(duration)
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    result = f"{minutes}:{remaining_seconds}"
    return result


# ───────────────────────────────
# Module Loading System
# ───────────────────────────────
def load_modules():
    """Load all modules dynamically"""
    global IMPORTED, MIGRATEABLE, HELPABLE, STATS, USER_INFO
    global DATA_IMPORT, DATA_EXPORT, CHAT_SETTINGS, USER_SETTINGS
    
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


# Load all modules
load_modules()


# ───────────────────────────────
# Helper Functions
# ───────────────────────────────
async def send_help(chat_id, text, keyboard=None):
    """Send help message - Now async for PTB v22"""
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    
    await application.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        reply_markup=keyboard,
    )


# ───────────────────────────────
# Main Handler Functions - PTB v22
# ───────────────────────────────

async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Test function"""
    await update.effective_message.reply_text("This person edited a message")
    print(update.effective_message)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    args = context.args
    chat = update.effective_chat
    
    if update.effective_chat.type == "private":
        if len(args) >= 1:
            if args[0].lower() == "help":
                await send_help(update.effective_chat.id, HELP_STRINGS)
            elif args[0].lower().startswith("help_"):
                mod = args[0].lower().split("_", 1)[1]
                if mod not in HELPABLE:
                    return
                    
                await send_help(
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
            elif args[0].lower().startswith("stngs_"):
                match = re.match("stngs_(.*)", args[0].lower())
                chat = await context.bot.get_chat(match.group(1))

                if is_user_admin(chat, update.effective_user.id):
                    await send_settings(match.group(1), update.effective_user.id, False)
                else:
                    await send_settings(match.group(1), update.effective_user.id, True)

            elif args[0][1:].isdigit() and "rules" in IMPORTED:
                await IMPORTED["rules"].send_rules(update, args[0], from_pm=True)
        else:
            await update.effective_message.reply_text(
                text=PM_START_TEXT,
                reply_markup=PM_START_BUTTON,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=False,
            )
    else:
        await update.effective_message.reply_text(
            text=GROUP_START_TEXT,
            parse_mode=ParseMode.HTML,
            reply_markup=GROUP_START_BUTTON,
        )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else
    LOGGER.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb = "".join(tb_list)

    # Build the message with some markup and additional information
    if update:
        message = (
            "An exception was raised while handling an update\n"
            "<pre>update = {}</pre>\n\n"
            "<pre>{}</pre>"
        ).format(
            html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False)),
            html.escape(tb),
        )
    else:
        message = f"An exception was raised\n<pre>{html.escape(tb)}</pre>"

    if len(message) >= 4096:
        message = message[:4096]
    
    # Send the message
    try:
        await context.bot.send_message(
            chat_id=OWNER_ID, 
            text=message, 
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        LOGGER.error(f"Failed to send error message: {e}")


async def error_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle specific error types"""
    try:
        raise context.error
    except BadRequest:
        pass
        # remove update.message.chat_id from conversation list
    except TimedOut:
        pass
        # handle slow connection problems
    except NetworkError:
        pass
        # handle other connection problems
    except ChatMigrated:
        pass
        # the chat_id of a group has changed, use e.new_chat_id instead
    except TelegramError:
        pass


async def help_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle help button callbacks"""
    query = update.callback_query
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)

    try:
        if mod_match:
            module = mod_match.group(1)
            text = (
                HELP_MODULE_TEXT.format(HELPABLE[module].__mod_name__)
                + HELPABLE[module].__help__
            )
            button = [[InlineKeyboardButton("🔙 Back", callback_data="help_back")]]
            
            if hasattr(HELPABLE[module], "__helpbtns__"):
                button = HELPABLE[module].__helpbtns__
                
            await query.message.edit_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(button),
            )

        elif prev_match:
            curr_page = int(prev_match.group(1))
            await query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(curr_page - 1, HELPABLE, "help")
                ),
            )

        elif next_match:
            next_page = int(next_match.group(1))
            await query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(next_page + 1, HELPABLE, "help")
                ),
            )

        elif back_match:
            await query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, HELPABLE, "help")
                ),
            )

        # ensure no spinny white circle
        await context.bot.answer_callback_query(query.id)
    except BadRequest:
        pass

async def ghelp_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle group help button callbacks"""
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
            button = [[InlineKeyboardButton("🔙 Back", callback_data="ghelp_back")]]
            
            if hasattr(HELPABLE[module], "__helpbtns__"):
                button = HELPABLE[module].__helpbtns__
                
            await query.message.edit_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(button),
            )

        elif prev_match:
            curr_page = int(prev_match.group(1))
            await query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    gpaginate_modules(curr_page - 1, HELPABLE, "ghelp")
                ),
            )

        elif next_match:
            next_page = int(next_match.group(1))
            await query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    gpaginate_modules(next_page + 1, HELPABLE, "ghelp")
                ),
            )

        elif back_match:
            await query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    gpaginate_modules(0, HELPABLE, "ghelp")
                ),
            )

        # ensure no spinny white circle
        await context.bot.answer_callback_query(query.id)
    except BadRequest:
        pass


async def merissa_about_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle about callback queries"""
    query = update.callback_query
    
    if query.data == "merissa_":
        await query.message.edit_text(
            text=HELP_STRINGS,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=PM_ABOUT_BUTTON,
        )
    elif query.data == "merissa_back":
        await query.message.edit_text(
            text=PM_START_TEXT,
            reply_markup=PM_START_BUTTON,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )
    elif query.data == "merissa_about":
        await query.message.edit_text(
            text=PM_ABOUT_TEXT,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="🔙 Back", callback_data="merissa_")]]
            ),
        )

    elif query.data == "merissa_source":
        await query.message.reply_sticker(
            "CAACAgUAAxkBAAJRAWLx-zmJ62FNVR9gnl4w22X5qRlqAAKyBAADwEBWQxLxqPtRziMpBA"
        )
        await query.message.delete()

    elif query.data == "merissa_latestup":
        await query.message.edit_text(
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
        await query.message.edit_text(
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
        await query.message.edit_text(
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
        await query.message.edit_text(
            text=PM_SUPPORT_TEXT,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=PM_SUPPORT_BUTTON,
        )
    elif query.data == "merissa_setting":
        await query.message.edit_text(
            text="Choose where you want help section using below Button",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=GROUP_HELP_BUTTON,
        )
    elif query.data == "merissa_private":
        userid = query.from_user.id
        try:
            await send_help(
                userid,
                text=HELP_STRINGS,
            )
            await query.answer("Help Menu Sent in Private Chat", show_alert=True)
        except:
            await query.answer("Unblock MerissaRobot and Try Again", show_alert=True)

    elif query.data == "merissa_donate":
        await query.message.edit_text(
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


async def Source_about_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle source callback queries"""
    query = update.callback_query
    if query.data == "source_":
        await query.message.edit_text(
            text="This advance command for Musicplayer."
            "\n\nCommand for admins only."
            "\n • `/reload` - For refreshing the adminlist."
            "\n • `/pause` - To pause the playback."
            "\n • `/resume` - To resuming the playback You've paused."
            "\n • `/skip` - To skipping the player."
            "\n • `/end` - For end the playback."
            "\n • `/musicplayer <on/off>` - Toggle for turn ON or turn OFF the musicplayer."
            "\n\nCommand for all members."
            "\n • `/play` <query /reply audio> - Playing music via YouTube."
            "\n • `/playlist` - To playing a playlist of groups or your personal playlist",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="Go Back", callback_data="merissa_")]]
            ),
        )
    elif query.data == "source_back":
        await query.message.edit_text(
            PM_START_TEXT,
            reply_markup=PM_START_BUTTON,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )


async def get_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle help command"""
    chat = update.effective_chat
    args = update.effective_message.text.split(None, 1)

    # ONLY send help in PM
    if chat.type != chat.PRIVATE:
        if len(args) >= 2 and any(args[1].lower().split(" ")[0] == x for x in HELPABLE):
            module = args[1].lower()
            await update.effective_message.reply_text(
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
            
        await update.effective_message.reply_text(
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
        await send_help(
            chat.id,
            text,
            InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="🔙 Back", callback_data="help_back")]]
            ),
        )
    else:
        await send_help(chat.id, HELP_STRINGS)


async def send_settings(chat_id, user_id, user=False):
    """Send settings message"""
    if user:
        if USER_SETTINGS:
            settings = "\n\n".join(
                "*{}*:\n{}".format(mod.__mod_name__, mod.__user_settings__(user_id))
                for mod in USER_SETTINGS.values()
            )
            await application.bot.send_message(
                user_id,
                text="Which module would you like to check {}'s settings for?"
                + "\n\n"
                + settings,
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            await application.bot.send_message(
                user_id,
                "Seems like there aren't any user specific settings available :'(",
                parse_mode=ParseMode.MARKDOWN,
            )
    else:
        if CHAT_SETTINGS:
            chat = await application.bot.get_chat(chat_id)
            await application.bot.send_message(
                user_id,
                text=f"Settings for {chat.title}",
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )
        else:
            await application.bot.send_message(
                user_id,
                "Seems like there aren't any chat settings available :'(\nSend this "
                "in a group chat you're admin in to find its current settings!",
                parse_mode=ParseMode.MARKDOWN,
            )


async def settings_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle settings button callbacks"""
    query = update.callback_query
    user = update.effective_user
    bot = context.bot
    mod_match = re.match(r"stngs_module\((.+?),(.+?)\)", query.data)
    prev_match = re.match(r"stngs_prev\((.+?),(.+?)\)", query.data)
    next_match = re.match(r"stngs_next\((.+?),(.+?)\)", query.data)
    back_match = re.match(r"stngs_back\((.+?)\)", query.data)
    
    try:
        if mod_match:
            chat_id = mod_match.group(1)
            module = mod_match.group(2)
            chat = await bot.get_chat(chat_id)
            text = "*{}* has the following settings for the *{}* module:\n\n".format(
                escape_markdown(chat.title), CHAT_SETTINGS[module].__mod_name__
            ) + CHAT_SETTINGS[module].__chat_settings__(chat_id, user.id)
            await query.message.reply_text(
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
            chat = await bot.get_chat(chat_id)
            await query.message.reply_text(
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
            chat = await bot.get_chat(chat_id)
            await query.message.reply_text(
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
            chat = await bot.get_chat(chat_id)
            await query.message.reply_text(
                text="Hi there! There are quite a few settings for {} - go ahead and pick what you're interested in.".format(
                    escape_markdown(chat.title)
                ),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )

        # ensure no spinny white circle
        await bot.answer_callback_query(query.id)
        await query.message.delete()
    except BadRequest as excp:
        if excp.message not in [
            "Message is not modified",
            "Query_id_invalid",
            "Message can't be deleted",
        ]:
            LOGGER.exception("Exception in settings buttons. %s", str(query.data))


async def get_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle settings command"""
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message

    # ONLY send settings in PM
    if chat.type != chat.PRIVATE:
        if is_user_admin(chat, user.id):
            text = "Click here to get this chat's settings, as well as yours."
            await msg.reply_text(
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
        await send_settings(chat.id, user.id, True)


async def migrate_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle chat migration"""
    msg = update.effective_message
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


# ───────────────────────────────
# Bot Initialization and Main Function
# ───────────────────────────────

async def initiate_clients():
    """Initialize all clients"""
    try:
        # Start pyrogram clients
        await pbot.start()
        LOGGER.info("Pyrogram Started")
        
        await user.start()
        LOGGER.info("Userbot Started")
        
        await pytgcalls.start()
        LOGGER.info("Pytgcalls Started")
        
        # Start telethon
        await telethn.start(bot_token=TOKEN)
        LOGGER.info("Telethon Started")
        
        # Send startup messages
        try:
            await pbot.send_message(-1001446814207, "Bot Started")
            await user.send_message(-1001446814207, "Assistant Started")
        except Exception as e:
            LOGGER.error(f"Failed to send startup messages: {e}")
            
    except FloodWait as e:
        LOGGER.info(f"FloodWait: Have to wait {e.value} seconds")
        await asyncio.sleep(e.value)
        await initiate_clients()
    except FloodWaitError as e:
        LOGGER.info(f"Telethon FloodWait: Have to wait {e.seconds} seconds")
        await asyncio.sleep(e.seconds)
        await initiate_clients()


async def setup_handlers():
    """Setup all handlers"""
    # Command handlers
    application.add_handler(CommandHandler("test", test))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", get_help))
    application.add_handler(CommandHandler("settings", get_settings))
    
    # Callback query handlers
    application.add_handler(CallbackQueryHandler(help_button, pattern=r"help_.*"))
    application.add_handler(CallbackQueryHandler(ghelp_button, pattern=r"ghelp_.*"))
    application.add_handler(CallbackQueryHandler(settings_button, pattern=r"stngs_"))
    application.add_handler(CallbackQueryHandler(merissa_about_callback, pattern=r"merissa_"))
    application.add_handler(CallbackQueryHandler(Source_about_callback, pattern=r"source_"))
    
    # Message handlers
    application.add_handler(MessageHandler(filters.StatusUpdate.MIGRATE, migrate_chats))
    
    # Error handlers
    application.add_error_handler(error_handler)

async def main():
    try:
        LOGGER.info("Successfully loaded Modules: " + str(ALL_MODULES))

        # Initialize all clients (ensure they start in current loop)
        await initiate_clients()

        # Setup handlers
        await setup_handlers()

        # Initialize application
        await application.initialize()
        await application.start()

        LOGGER.info("PTB Started Successfully")
        LOGGER.info("MerissaRobot Started Successfully")

        # Send startup notification
        try:
            await application.bot.send_message(2030709195, "Merissa Started")
        except Exception as e:
            LOGGER.error(f"Failed to send startup notification: {e}")

        # Run PTB + other clients concurrently on SAME loop
        await asyncio.gather(
            application.run_polling(
                stop_signals=None,  # asyncio handles signals
                drop_pending_updates=True,
                allowed_updates=Update.ALL_TYPES,
            ),
            pbot.start(),     # Pyrogram bot
            user.start(),     # Userbot
            telethn.start(),  # Telethon
            pytgcalls.start() # PyTgCalls
        )

    except Exception as e:
        LOGGER.error(f"Error in main: {e}")
        raise
    finally:
        # Cleanup
        try:
            if application.running:
                await application.stop()
            await application.shutdown()

            if hasattr(pbot, "is_connected") and pbot.is_connected:
                await pbot.stop()
            if hasattr(user, "is_connected") and user.is_connected:
                await user.stop()
            if hasattr(pytgcalls, "stop"):
                await pytgcalls.stop()
            if hasattr(telethn, "is_connected") and telethn.is_connected():
                await telethn.disconnect()

            LOGGER.info("Bot stopped successfully")
        except Exception as e:
            LOGGER.error(f"Error during cleanup: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        LOGGER.info("Bot stopped by user")
    except Exception as e:
        LOGGER.error(f"Fatal error: {e}")
        import sys
        sys.exit(1)
