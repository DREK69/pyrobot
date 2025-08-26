import random
import re
from html import escape
from typing import Optional

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, Message, Chat
from telegram.constants import MessageLimit, ParseMode
from telegram.error import BadRequest
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    filters,
    MessageHandler,
)
from telegram.helpers import escape_markdown, mention_html

from MerissaRobot import DRAGONS, LOGGER, application
from MerissaRobot.Database.sql.cust_filters_sql import CustomFilters as DBCustomFilters
from MerissaRobot.Handler.ptb.alternate import send_message, typing_action
from MerissaRobot.Handler.ptb.chat_status import user_admin
from MerissaRobot.Handler.ptb.extraction import extract_text
from MerissaRobot.Handler.ptb.filters import CustomFilters
from MerissaRobot.Handler.ptb.handlers import MessageHandlerChecker
from MerissaRobot.Handler.ptb.misc import build_keyboard_parser
from MerissaRobot.Handler.ptb.msg_types import get_filter_type
from MerissaRobot.Handler.ptb.string_handling import (
    button_markdown_parser,
    escape_invalid_curly_brackets,
    markdown_to_html,
    split_quotes,
)
from MerissaRobot.Modules.connection import connected
from MerissaRobot.Modules.disable import DisableAbleCommandHandler

HANDLER_GROUP = 10


# Enum function mapping - async version
async def get_enum_func_map(bot):
    return {
        sql.Types.TEXT.value: bot.send_message,
        sql.Types.BUTTON_TEXT.value: bot.send_message,
        sql.Types.STICKER.value: bot.send_sticker,
        sql.Types.DOCUMENT.value: bot.send_document,
        sql.Types.PHOTO.value: bot.send_photo,
        sql.Types.AUDIO.value: bot.send_audio,
        sql.Types.VOICE.value: bot.send_voice,
        sql.Types.VIDEO.value: bot.send_video,
    }


@typing_action
async def list_handlers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    conn = connected(context.bot, update, chat, user.id, need_admin=False)
    if conn is not False:
        chat_id = conn
        chat_obj = await context.bot.get_chat(conn)
        chat_name = chat_obj.title
        filter_list = "*Filter in {}:*\n"
    else:
        chat_id = update.effective_chat.id
        if chat.type == "private":
            chat_name = "Local filters"
            filter_list = "*local filters:*\n"
        else:
            chat_name = chat.title
            filter_list = "*Filters in {}*:\n"

    all_handlers = sql.get_chat_triggers(chat_id)

    if not all_handlers:
        await send_message(
            update.effective_message, "No filters saved in {}!".format(chat_name)
        )
        return

    for keyword in all_handlers:
        entry = " • `{}`\n".format(escape_markdown(keyword, version=2))
        if len(entry) + len(filter_list) > MessageLimit.MAX_TEXT_LENGTH:
            await send_message(
                update.effective_message,
                filter_list.format(chat_name),
                parse_mode=ParseMode.MARKDOWN_V2,
            )
            filter_list = entry
        else:
            filter_list += entry

    await send_message(
        update.effective_message,
        filter_list.format(chat_name),
        parse_mode=ParseMode.MARKDOWN_V2,
    )


@user_admin
@typing_action
async def filters_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message
    args = msg.text.split(None, 1)

    conn = connected(context.bot, update, chat, user.id)
    if conn is not False:
        chat_id = conn
        chat_obj = await context.bot.get_chat(conn)
        chat_name = chat_obj.title
    else:
        chat_id = update.effective_chat.id
        if chat.type == "private":
            chat_name = "local filters"
        else:
            chat_name = chat.title

    if not msg.reply_to_message and len(args) < 2:
        await send_message(
            update.effective_message,
            "Please provide keyboard keyword for this filter to reply with!",
        )
        return

    if msg.reply_to_message:
        if len(args) < 2:
            await send_message(
                update.effective_message,
                "Please provide keyword for this filter to reply with!",
            )
            return
        else:
            keyword = args[1]
    else:
        extracted = split_quotes(args[1])
        if len(extracted) < 1:
            return
        keyword = extracted[0].lower()

    # Remove existing handler if exists
    for handler in application.handlers.get(HANDLER_GROUP, []):
        if hasattr(handler, 'filters') and handler.filters == (keyword, chat_id):
            application.remove_handler(handler, HANDLER_GROUP)

    text, file_type, file_id = get_filter_type(msg)
    buttons = []
    
    if not msg.reply_to_message and len(extracted) >= 2:
        offset = len(extracted[1]) - len(msg.text)
        
        # Extract entities
        entities_dict = {}
        if msg.entities:
            for entity in msg.entities:
                entity_text = msg.text[entity.offset:entity.offset + entity.length]
                entities_dict[entity] = entity_text
        
        text, buttons = button_markdown_parser(
            extracted[1], entities=entities_dict, offset=offset
        )
        text = text.strip()
        if not text:
            await send_message(
                update.effective_message,
                "There is no note message - You can't JUST have buttons, you need a message to go with it!",
            )
            return

    elif msg.reply_to_message and len(args) >= 2:
        if msg.reply_to_message.text:
            text_to_parsing = msg.reply_to_message.text
        elif msg.reply_to_message.caption:
            text_to_parsing = msg.reply_to_message.caption
        else:
            text_to_parsing = ""
        
        offset = len(text_to_parsing)
        
        # Extract entities from reply message
        entities_dict = {}
        if msg.reply_to_message.entities:
            for entity in msg.reply_to_message.entities:
                entity_text = text_to_parsing[entity.offset:entity.offset + entity.length]
                entities_dict[entity] = entity_text
        elif msg.reply_to_message.caption_entities:
            for entity in msg.reply_to_message.caption_entities:
                entity_text = text_to_parsing[entity.offset:entity.offset + entity.length]
                entities_dict[entity] = entity_text
        
        text, buttons = button_markdown_parser(
            text_to_parsing, entities=entities_dict, offset=offset
        )
        text = text.strip()

    elif not text and not file_type:
        await send_message(
            update.effective_message,
            "Please provide keyword for this filter reply with!",
        )
        return

    elif msg.reply_to_message:
        if msg.reply_to_message.text:
            text_to_parsing = msg.reply_to_message.text
        elif msg.reply_to_message.caption:
            text_to_parsing = msg.reply_to_message.caption
        else:
            text_to_parsing = ""
        
        offset = len(text_to_parsing)
        
        # Extract entities from reply message
        entities_dict = {}
        if msg.reply_to_message.entities:
            for entity in msg.reply_to_message.entities:
                entity_text = text_to_parsing[entity.offset:entity.offset + entity.length]
                entities_dict[entity] = entity_text
        elif msg.reply_to_message.caption_entities:
            for entity in msg.reply_to_message.caption_entities:
                entity_text = text_to_parsing[entity.offset:entity.offset + entity.length]
                entities_dict[entity] = entity_text
        
        text, buttons = button_markdown_parser(
            text_to_parsing, entities=entities_dict, offset=offset
        )
        text = text.strip()
        if (msg.reply_to_message.text or msg.reply_to_message.caption) and not text:
            await send_message(
                update.effective_message,
                "There is no note message - You can't JUST have buttons, you need a message to go with it!",
            )
            return

    else:
        await send_message(update.effective_message, "Invalid filter!")
        return

    add = await addnew_filter(update, chat_id, keyword, text, file_type, file_id, buttons)

    if add is True:
        await send_message(
            update.effective_message,
            "Saved filter '{}' in *{}*!".format(keyword, chat_name),
            parse_mode=ParseMode.MARKDOWN_V2,
        )


@user_admin
@typing_action
async def stop_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    args = update.effective_message.text.split(None, 1)

    conn = connected(context.bot, update, chat, user.id)
    if conn is not False:
        chat_id = conn
        chat_obj = await context.bot.get_chat(conn)
        chat_name = chat_obj.title
    else:
        chat_id = update.effective_chat.id
        if chat.type == "private":
            chat_name = "Local filters"
        else:
            chat_name = chat.title

    if len(args) < 2:
        await send_message(update.effective_message, "What should i stop?")
        return

    chat_filters = sql.get_chat_triggers(chat_id)

    if not chat_filters:
        await send_message(update.effective_message, "No filters active here!")
        return

    for keyword in chat_filters:
        if keyword == args[1]:
            sql.remove_filter(chat_id, args[1])
            await send_message(
                update.effective_message,
                "Okay, I'll stop replying to that filter in *{}*.".format(chat_name),
                parse_mode=ParseMode.MARKDOWN_V2,
            )
            return

    await send_message(
        update.effective_message,
        "That's not a filter - Click: /filters to get currently active filters.",
    )

async def reply_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat: Optional[Chat] = update.effective_chat
    message: Optional[Message] = update.effective_message

    if not update.effective_user or update.effective_user.id == 777000:
        return
    
    to_match = extract_text(message)
    if not to_match:
        return

    chat_filters = sql.get_chat_triggers(chat.id)
    enum_func_map = await get_enum_func_map(context.bot)
    
    for keyword in chat_filters:
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, to_match, flags=re.IGNORECASE):
            if MessageHandlerChecker.check_user(update.effective_user.id):
                return
            
            filt = sql.get_filter(chat.id, keyword)
            if filt.reply == "there is should be a new reply":
                buttons = sql.get_buttons(chat.id, filt.keyword)
                keyb = build_keyboard_parser(context.bot, chat.id, buttons)
                keyboard = InlineKeyboardMarkup(keyb)

                VALID_WELCOME_FORMATTERS = [
                    "first", "last", "fullname", "username", "id", "chatname", "mention",
                ]
                
                if filt.reply_text:
                    if "%%%" in filt.reply_text:
                        split = filt.reply_text.split("%%%")
                        if all(split):
                            text = random.choice(split)
                        else:
                            text = filt.reply_text
                    else:
                        text = filt.reply_text
                        
                    if text.startswith("~!") and text.endswith("!~"):
                        sticker_id = text.replace("~!", "").replace("!~", "")
                        try:
                            await context.bot.send_sticker(
                                chat.id,
                                sticker_id,
                                reply_to_message_id=message.message_id,
                            )
                            return
                        except BadRequest as excp:
                            if (
                                excp.message
                                == "Wrong remote file identifier specified: wrong padding in the string"
                            ):
                                await context.bot.send_message(
                                    chat.id,
                                    "Message couldn't be sent, Is the sticker id valid?",
                                )
                                return
                            else:
                                LOGGER.exception("Error in filters: " + excp.message)
                                return
                    
                    valid_format = escape_invalid_curly_brackets(
                        text, VALID_WELCOME_FORMATTERS
                    )
                    if valid_format:
                        filtext = valid_format.format(
                            first=escape(message.from_user.first_name),
                            last=escape(
                                message.from_user.last_name
                                or message.from_user.first_name
                            ),
                            fullname=" ".join(
                                [
                                    escape(message.from_user.first_name),
                                    escape(message.from_user.last_name),
                                ]
                                if message.from_user.last_name
                                else [escape(message.from_user.first_name)]
                            ),
                            username=(
                                "@" + escape(message.from_user.username)
                                if message.from_user.username
                                else mention_html(
                                    message.from_user.id, message.from_user.first_name
                                )
                            ),
                            mention=mention_html(
                                message.from_user.id, message.from_user.first_name
                            ),
                            chatname=(
                                escape(message.chat.title)
                                if message.chat.type != "private"
                                else escape(message.from_user.first_name)
                            ),
                            id=message.from_user.id,
                        )
                    else:
                        filtext = ""
                else:
                    filtext = ""

                if filt.file_type in (sql.Types.BUTTON_TEXT, sql.Types.TEXT):
                    try:
                        await context.bot.send_message(
                            chat.id,
                            markdown_to_html(filtext),
                            reply_to_message_id=message.message_id,
                            parse_mode=ParseMode.HTML,
                            disable_web_page_preview=True,
                            reply_markup=keyboard,
                        )
                    except BadRequest as excp:
                        error_catch = get_exception(excp, filt, chat)
                        if error_catch == "noreply":
                            try:
                                await context.bot.send_message(
                                    chat.id,
                                    markdown_to_html(filtext),
                                    parse_mode=ParseMode.HTML,
                                    disable_web_page_preview=True,
                                    reply_markup=keyboard,
                                )
                            except BadRequest as excp:
                                LOGGER.exception("Error in filters: " + excp.message)
                                await send_message(
                                    update.effective_message,
                                    get_exception(excp, filt, chat),
                                )
                        else:
                            try:
                                await send_message(
                                    update.effective_message,
                                    get_exception(excp, filt, chat),
                                )
                            except BadRequest as excp:
                                LOGGER.exception(
                                    "Failed to send message: " + excp.message
                                )
                else:
                    try:
                        func = enum_func_map[filt.file_type]
                        if func == context.bot.send_sticker:
                            await func(
                                chat.id,
                                filt.file_id,
                                reply_to_message_id=message.message_id,
                                reply_markup=keyboard,
                            )
                        else:
                            await func(
                                chat.id,
                                filt.file_id,
                                caption=markdown_to_html(filtext),
                                reply_to_message_id=message.message_id,
                                parse_mode=ParseMode.HTML,
                                reply_markup=keyboard,
                            )
                    except BadRequest as excp:
                        LOGGER.exception("Failed to send message: " + excp.message)
                break
            else:
                # Legacy filter handling
                if filt.is_sticker:
                    await message.reply_sticker(filt.reply)
                elif filt.is_document:
                    await message.reply_document(filt.reply)
                elif filt.is_image:
                    await message.reply_photo(filt.reply)
                elif filt.is_audio:
                    await message.reply_audio(filt.reply)
                elif filt.is_voice:
                    await message.reply_voice(filt.reply)
                elif filt.is_video:
                    await message.reply_video(filt.reply)
                elif filt.has_markdown:
                    buttons = sql.get_buttons(chat.id, filt.keyword)
                    keyb = build_keyboard_parser(context.bot, chat.id, buttons)
                    keyboard = InlineKeyboardMarkup(keyb)

                    try:
                        await send_message(
                            update.effective_message,
                            filt.reply,
                            parse_mode=ParseMode.MARKDOWN,
                            disable_web_page_preview=True,
                            reply_markup=keyboard,
                        )
                    except BadRequest as excp:
                        if excp.message == "Unsupported url protocol":
                            try:
                                await send_message(
                                    update.effective_message,
                                    "You seem to be trying to use an unsupported url protocol. "
                                    "Telegram doesn't support buttons for some protocols, such as tg://. Please try "
                                    "again...",
                                )
                            except BadRequest as excp:
                                LOGGER.exception("Error in filters: " + excp.message)
                        elif excp.message == "Reply message not found":
                            try:
                                await context.bot.send_message(
                                    chat.id,
                                    filt.reply,
                                    parse_mode=ParseMode.MARKDOWN,
                                    disable_web_page_preview=True,
                                    reply_markup=keyboard,
                                )
                            except BadRequest as excp:
                                LOGGER.exception("Error in filters: " + excp.message)
                        else:
                            try:
                                await send_message(
                                    update.effective_message,
                                    "This message couldn't be sent as it's incorrectly formatted.",
                                )
                            except BadRequest as excp:
                                LOGGER.exception("Error in filters: " + excp.message)
                            LOGGER.warning(
                                "Message %s could not be parsed", str(filt.reply)
                            )
                            LOGGER.exception(
                                "Could not parse filter %s in chat %s",
                                str(filt.keyword),
                                str(chat.id),
                            )
                else:
                    # LEGACY - all new filters will have has_markdown set to True.
                    try:
                        await send_message(update.effective_message, filt.reply)
                    except BadRequest as excp:
                        LOGGER.exception("Error in filters: " + excp.message)
                break


async def rmall_filters(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    member = await chat.get_member(user.id)
    
    if member.status != "creator" and user.id not in DRAGONS:
        await update.effective_message.reply_text(
            "Only the chat owner can clear all notes at once."
        )
    else:
        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Stop all filters", callback_data="filters_rmall"
                    )
                ],
                [InlineKeyboardButton(text="Cancel", callback_data="filters_cancel")],
            ]
        )
        await update.effective_message.reply_text(
            f"Are you sure you would like to stop ALL filters in {chat.title}? This action cannot be undone.",
            reply_markup=buttons,
            parse_mode=ParseMode.MARKDOWN,
        )


async def rmall_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat = update.effective_chat
    msg = update.effective_message
    member = await chat.get_member(query.from_user.id)
    
    if query.data == "filters_rmall":
        if member.status == "creator" or query.from_user.id in DRAGONS:
            allfilters = sql.get_chat_triggers(chat.id)
            if not allfilters:
                await msg.edit_text("No filters in this chat, nothing to stop!")
                return

            count = 0
            filterlist = []
            for x in allfilters:
                count += 1
                filterlist.append(x)

            for i in filterlist:
                sql.remove_filter(chat.id, i)

            await msg.edit_text(f"Cleaned {count} filters in {chat.title}")

        elif member.status == "administrator":
            await query.answer("Only owner of the chat can do this.")
        elif member.status == "member":
            await query.answer("You need to be admin to do this.")
            
    elif query.data == "filters_cancel":
        if member.status == "creator" or query.from_user.id in DRAGONS:
            await msg.edit_text("Clearing of all filters has been cancelled.")
            return
        elif member.status == "administrator":
            await query.answer("Only owner of the chat can do this.")
        elif member.status == "member":
            await query.answer("You need to be admin to do this.")


def get_exception(excp: BadRequest, filt, chat) -> str:
    if excp.message == "Unsupported url protocol":
        return "You seem to be trying to use the URL protocol which is not supported. Telegram does not support key for multiple protocols, such as tg: //. Please try again!"
    elif excp.message == "Reply message not found":
        return "noreply"
    else:
        LOGGER.warning("Message %s could not be parsed", str(filt.reply))
        LOGGER.exception(
            "Could not parse filter %s in chat %s", str(filt.keyword), str(chat.id)
        )
        return "This data could not be sent because it is incorrectly formatted."


async def addnew_filter(update: Update, chat_id: int, keyword: str, text: str, 
                       file_type, file_id: str, buttons) -> bool:
    msg = update.effective_message
    totalfilt = sql.get_chat_triggers(chat_id)
    
    if len(totalfilt) >= 150:
        await msg.reply_text("This group has reached its max filters limit of 150.")
        return False
    else:
        sql.new_add_filter(chat_id, keyword, text, file_type, file_id, buttons)
        return True


def __stats__() -> str:
    return "× {} filters, across {} chats.".format(sql.num_filters(), sql.num_chats())


def __import_data__(chat_id: int, data: dict):
    filters_data = data.get("filters", {})
    for trigger in filters_data:
        sql.add_to_blacklist(chat_id, trigger)


def __migrate__(old_chat_id: int, new_chat_id: int):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id: int, user_id: int) -> str:
    cust_filters = sql.get_chat_triggers(chat_id)
    return "There are `{}` custom filters here.".format(len(cust_filters))


__help__ = """
❂ /filters*:* List all active filters saved in the chat.

*Admin only:*
❂ /filter <keyword> <reply message>*:* Add a filter to this chat. The bot will now reply that message whenever 'keyword'\
is mentioned. If you reply to a sticker with a keyword, the bot will reply with that sticker. NOTE: all filter \
keywords are in lowercase. If you want your keyword to be a sentence, use quotes. eg: /filter "hey there" How you \
doin?

 Separate diff replies by `%%%` to get random replies
 *Example:* 
 `/filter "filtername"
 Reply 1
 %%%
 Reply 2
 %%%
 Reply 3`

❂ /stop <filter keyword>*:* Stop that filter.

*Chat creator only:*
❂ /removeallfilters*:* Remove all chat filters at once.

*Note*: Filters also support markdown formatters like: {first}, {last} etc.. and buttons.
Check /markdownhelp to know more!
"""

__mod_name__ = "Filters 📝"

# PTB v22 Handler definitions
FILTER_HANDLER = CommandHandler("filter", filters_command)
STOP_HANDLER = CommandHandler("stop", stop_filter)
RMALLFILTER_HANDLER = CommandHandler(
    "removeallfilters", rmall_filters, filters=filters.ChatType.GROUPS
)
RMALLFILTER_CALLBACK = CallbackQueryHandler(rmall_callback, pattern=r"filters_.*")
LIST_HANDLER = DisableAbleCommandHandler("filters", list_handlers, admin_ok=True)

# Fix the CustomFilters reference - use the telegram bot's CustomFilters, not your DB model
CUST_FILTER_HANDLER = MessageHandler(
    filters.TEXT & ~filters.UpdateType.EDITED_MESSAGE,  # Use filters.TEXT instead
    reply_filter,
)

# Add handlers to application
application.add_handler(FILTER_HANDLER)
application.add_handler(STOP_HANDLER)
application.add_handler(LIST_HANDLER)
application.add_handler(CUST_FILTER_HANDLER, HANDLER_GROUP)
application.add_handler(RMALLFILTER_HANDLER)
application.add_handler(RMALLFILTER_CALLBACK)

__handlers__ = [
    FILTER_HANDLER,
    STOP_HANDLER,
    LIST_HANDLER,
    (CUST_FILTER_HANDLER, HANDLER_GROUP),
    RMALLFILTER_HANDLER,
    RMALLFILTER_CALLBACK,
]
