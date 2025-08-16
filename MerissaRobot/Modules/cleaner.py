import html

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from telegram.constants import ParseMode

from MerissaRobot import ALLOW_EXCL, CustomCommandHandler, application
from MerissaRobot.Database.sql import cleaner_sql as sql
from MerissaRobot.Handler.ptb.chat_status import (
    bot_can_delete,
    connection_status,
    dev_plus,
    user_admin,
)
from MerissaRobot.Modules.disable import DisableAbleCommandHandler

CMD_STARTERS = ("/", "!") if ALLOW_EXCL else "/"
BLUE_TEXT_CLEAN_GROUP = 13
CommandHandlerList = (CommandHandler, CustomCommandHandler, DisableAbleCommandHandler)
command_list = [
    "cleanblue",
    "ignoreblue",
    "unignoreblue",
    "listblue",
    "ungignoreblue",
    "gignoreblue",
    "start",
    "help",
    "settings",
    "donate",
    "stalk",
    "aka",
    "leaderboard",
]

# Get commands from application handlers
for group_id in application.handlers:
    for handler in application.handlers[group_id]:
        if any(isinstance(handler, cmd_handler) for cmd_handler in CommandHandlerList):
            if hasattr(handler, 'commands'):
                command_list.extend(handler.commands)
            elif hasattr(handler, 'command'):
                if isinstance(handler.command, list):
                    command_list.extend(handler.command)
                else:
                    command_list.append(handler.command)


async def clean_blue_text_must_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clean blue text commands that don't exist"""
    bot = context.bot
    chat = update.effective_chat
    message = update.effective_message
    
    if not message.text:
        return
    
    try:
        bot_member = await chat.get_member(bot.id)
        can_delete = bot_member.can_delete_messages
    except:
        can_delete = False
    
    if can_delete and sql.is_enabled(chat.id):
        fst_word = message.text.strip().split(None, 1)[0]

        if len(fst_word) > 1 and any(
            fst_word.startswith(start) for start in CMD_STARTERS
        ):
            command = fst_word[1:].split("@")
            chat = update.effective_chat

            ignored = sql.is_command_ignored(chat.id, command[0])
            if ignored:
                return

            if command[0] not in command_list:
                try:
                    await message.delete()
                except:
                    pass  # Ignore if we can't delete


@connection_status
@bot_can_delete
@user_admin
async def set_blue_text_must_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enable or disable blue text cleaning"""
    chat = update.effective_chat
    message = update.effective_message
    bot, args = context.bot, context.args
    
    if len(args) >= 1:
        val = args[0].lower()
        if val in ("off", "no"):
            sql.set_cleanbt(chat.id, False)
            reply = "Bluetext cleaning has been disabled for <b>{}</b>".format(
                html.escape(chat.title),
            )
            await message.reply_text(reply, parse_mode=ParseMode.HTML)

        elif val in ("yes", "on"):
            sql.set_cleanbt(chat.id, True)
            reply = "Bluetext cleaning has been enabled for <b>{}</b>".format(
                html.escape(chat.title),
            )
            await message.reply_text(reply, parse_mode=ParseMode.HTML)

        else:
            reply = "Invalid argument. Accepted values are 'yes', 'on', 'no', 'off'"
            await message.reply_text(reply)
    else:
        clean_status = sql.is_enabled(chat.id)
        clean_status = "Enabled" if clean_status else "Disabled"
        reply = "Bluetext cleaning for <b>{}</b> : <b>{}</b>".format(
            html.escape(chat.title),
            clean_status,
        )
        await message.reply_text(reply, parse_mode=ParseMode.HTML)


@user_admin
async def add_bluetext_ignore(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a command to the ignore list for blue text cleaning"""
    message = update.effective_message
    chat = update.effective_chat
    args = context.args
    
    if len(args) >= 1:
        val = args[0].lower()
        added = sql.chat_ignore_command(chat.id, val)
        if added:
            reply = "<b>{}</b> has been added to bluetext cleaner ignore list.".format(
                args[0],
            )
        else:
            reply = "Command is already ignored."
        await message.reply_text(reply, parse_mode=ParseMode.HTML)

    else:
        reply = "No command supplied to be ignored."
        await message.reply_text(reply)


@user_admin
async def remove_bluetext_ignore(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove a command from the ignore list for blue text cleaning"""
    message = update.effective_message
    chat = update.effective_chat
    args = context.args
    
    if len(args) >= 1:
        val = args[0].lower()
        removed = sql.chat_unignore_command(chat.id, val)
        if removed:
            reply = (
                "<b>{}</b> has been removed from bluetext cleaner ignore list.".format(
                    args[0],
                )
            )
        else:
            reply = "Command isn't ignored currently."
        await message.reply_text(reply, parse_mode=ParseMode.HTML)

    else:
        reply = "No command supplied to be unignored."
        await message.reply_text(reply)


@user_admin
async def add_bluetext_ignore_global(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a command to the global ignore list for blue text cleaning"""
    message = update.effective_message
    args = context.args
    
    if len(args) >= 1:
        val = args[0].lower()
        added = sql.global_ignore_command(val)
        if added:
            reply = "<b>{}</b> has been added to global bluetext cleaner ignore list.".format(
                args[0],
            )
        else:
            reply = "Command is already ignored."
        await message.reply_text(reply, parse_mode=ParseMode.HTML)

    else:
        reply = "No command supplied to be ignored."
        await message.reply_text(reply)


@dev_plus
async def remove_bluetext_ignore_global(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove a command from the global ignore list for blue text cleaning"""
    message = update.effective_message
    args = context.args
    
    if len(args) >= 1:
        val = args[0].lower()
        removed = sql.global_unignore_command(val)
        if removed:
            reply = "<b>{}</b> has been removed from global bluetext cleaner ignore list.".format(
                args[0],
            )
        else:
            reply = "Command isn't ignored currently."
        await message.reply_text(reply, parse_mode=ParseMode.HTML)

    else:
        reply = "No command supplied to be unignored."
        await message.reply_text(reply)


@dev_plus
async def bluetext_ignore_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all ignored commands for blue text cleaning"""
    message = update.effective_message
    chat = update.effective_chat

    global_ignored_list, local_ignore_list = sql.get_all_ignored(chat.id)
    text = ""

    if global_ignored_list:
        text = "The following commands are currently ignored globally from bluetext cleaning :\n"

        for x in global_ignored_list:
            text += f" - <code>{x}</code>\n"

    if local_ignore_list:
        text += "\nThe following commands are currently ignored locally from bluetext cleaning :\n"

        for x in local_ignore_list:
            text += f" - <code>{x}</code>\n"

    if text == "":
        text = "No commands are currently ignored from bluetext cleaning."
        await message.reply_text(text)
        return

    await message.reply_text(text, parse_mode=ParseMode.HTML)
    return


__help__ = """
 Blue text cleaner removes any made up commands that people send in your chat.

❂ /cleanblue <on/off/yes/no>*:* clean commands after sending
❂ /ignoreblue <word>*:* prevent auto cleaning of the command
❂ /unignoreblue <word>*:* remove prevent auto cleaning of the command
❂ /listblue*:* list currently whitelisted commands

 *Following are Disasters only commands, admins cannot use these:*

❂ /gignoreblue <word>*:* globally ignore bluetext cleaning of saved word across Merissa.
❂ /ungignoreblue <word>*:* remove said command from global cleaning list
"""

# PTB v22 Compatible Handlers
SET_CLEAN_BLUE_TEXT_HANDLER = CommandHandler(
    "cleanblue", set_blue_text_must_click
)
ADD_CLEAN_BLUE_TEXT_HANDLER = CommandHandler(
    "ignoreblue", add_bluetext_ignore
)
REMOVE_CLEAN_BLUE_TEXT_HANDLER = CommandHandler(
    "unignoreblue", remove_bluetext_ignore
)
ADD_CLEAN_BLUE_TEXT_GLOBAL_HANDLER = CommandHandler(
    "gignoreblue",
    add_bluetext_ignore_global,
)
REMOVE_CLEAN_BLUE_TEXT_GLOBAL_HANDLER = CommandHandler(
    "ungignoreblue",
    remove_bluetext_ignore_global,
)
LIST_CLEAN_BLUE_TEXT_HANDLER = CommandHandler(
    "listblue", bluetext_ignore_list
)
CLEAN_BLUE_TEXT_HANDLER = MessageHandler(
    filters.COMMAND & filters.ChatType.GROUPS,
    clean_blue_text_must_click,
)

# Add handlers to application
application.add_handler(SET_CLEAN_BLUE_TEXT_HANDLER)
application.add_handler(ADD_CLEAN_BLUE_TEXT_HANDLER)
application.add_handler(REMOVE_CLEAN_BLUE_TEXT_HANDLER)
application.add_handler(ADD_CLEAN_BLUE_TEXT_GLOBAL_HANDLER)
application.add_handler(REMOVE_CLEAN_BLUE_TEXT_GLOBAL_HANDLER)
application.add_handler(LIST_CLEAN_BLUE_TEXT_HANDLER)
application.add_handler(CLEAN_BLUE_TEXT_HANDLER, BLUE_TEXT_CLEAN_GROUP)

__mod_name__ = "Cleaner 🧹"
__handlers__ = [
    SET_CLEAN_BLUE_TEXT_HANDLER,
    ADD_CLEAN_BLUE_TEXT_HANDLER,
    REMOVE_CLEAN_BLUE_TEXT_HANDLER,
    ADD_CLEAN_BLUE_TEXT_GLOBAL_HANDLER,
    REMOVE_CLEAN_BLUE_TEXT_GLOBAL_HANDLER,
    LIST_CLEAN_BLUE_TEXT_HANDLER,
    (CLEAN_BLUE_TEXT_HANDLER, BLUE_TEXT_CLEAN_GROUP),
]
