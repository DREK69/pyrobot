import html
import re
from typing import Optional

import telegram
from telegram import (
    CallbackQuery,
    Chat,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    Update,
    User,
)
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
    CommandHandler,
    filters,
    MessageHandler,
)
from telegram.helpers import mention_html

from MerissaRobot import TIGERS, WOLVES, application
from MerissaRobot.Database.sql import warns_sql as sql
from MerissaRobot.Database.sql.approve_sql import is_approved
from MerissaRobot.Handler.ptb.chat_status import (
    bot_admin,
    can_restrict,
    is_user_admin,
    user_admin,
    user_admin_no_reply,
)
from MerissaRobot.Handler.ptb.extraction import (
    extract_text,
    extract_user,
    extract_user_and_text,
)
from MerissaRobot.Handler.ptb.filters import CustomFilters
from MerissaRobot.Handler.ptb.misc import split_message
from MerissaRobot.Handler.ptb.string_handling import split_quotes
from MerissaRobot.Modules.disable import DisableAbleCommandHandler
from MerissaRobot.Modules.log_channel import loggable

WARN_HANDLER_GROUP = 9
CURRENT_WARNING_FILTER_STRING = "<b>Current warning filters in this chat:</b>\n"


# Not async - utility function
async def warn(
    user: User, chat: Chat, reason: str, message: Message, warner: User = None
) -> str:
    if await is_user_admin(chat, user.id):
        # message.reply_text("Damn admins, They are too far to be One Punched!")
        return

    if user.id in TIGERS:
        if warner:
            await message.reply_text("🧜 **Tigers cant be warned.**")
        else:
            await message.reply_text(
                "🧜 **Tiger triggered an auto warn filter!**\n⚠️ I can't warn tigers but they should avoid abusing this."
            )
        return

    if user.id in WOLVES:
        if warner:
            await message.reply_text("🧜‍♂️ **Wolf disasters are warn immune.**")
        else:
            await message.reply_text(
                "🧜‍♂️ **Wolf Disaster triggered an auto warn filter!**\n⚠️ I can't warn wolves but they should avoid abusing this."
            )
        return

    if warner:
        warner_tag = mention_html(warner.id, warner.first_name)
    else:
        warner_tag = "Automated warn filter."

    limit, soft_warn = sql.get_warn_setting(chat.id)
    num_warns, reasons = sql.warn_user(user.id, chat.id, reason)
    
    if num_warns >= limit:
        sql.reset_warns(user.id, chat.id)
        if soft_warn:  # kick
            await chat.unban_member(user.id)
            reply = f"👢 {mention_html(user.id, user.first_name)} [<code>{user.id}</code>] **Kicked**"
        else:  # ban
            await chat.ban_member(user.id)
            reply = f"🔨 {mention_html(user.id, user.first_name)} [<code>{user.id}</code>] **Banned**"

        for warn_reason in reasons:
            reply += f"\n • {html.escape(warn_reason)}"

        keyboard = None
        log_reason = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#WARN_BAN\n"
            f"<b>Admin:</b> {warner_tag}\n"
            f"<b>User:</b> {mention_html(user.id, user.first_name)}\n"
            f"<b>Reason:</b> {reason}\n"
            f"<b>Counts:</b> <code>{num_warns}/{limit}</code>"
        )

    else:
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "❌ Remove Warn", callback_data="rm_warn({})".format(user.id)
                    )
                ]
            ]
        )

        reply = (
            f"⚠️ {mention_html(user.id, user.first_name)} [<code>{user.id}</code>]"
            f" **Warned** ({num_warns}/{limit})"
        )
        if reason:
            reply += f"\n📝 **Reason:** {html.escape(reason)}"

        log_reason = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#WARN\n"
            f"<b>Admin:</b> {warner_tag}\n"
            f"<b>User:</b> {mention_html(user.id, user.first_name)}\n"
            f"<b>Reason:</b> {reason}\n"
            f"<b>Counts:</b> <code>{num_warns}/{limit}</code>"
        )

    try:
        await message.reply_text(reply, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            await message.reply_text(
                reply, reply_markup=keyboard, parse_mode=ParseMode.HTML, reply_to_message_id=None
            )
        else:
            raise
    return log_reason


@user_admin_no_reply
@bot_admin
@loggable
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    query: Optional[CallbackQuery] = update.callback_query
    user: Optional[User] = update.effective_user
    match = re.match(r"rm_warn\((.+?)\)", query.data)
    
    if match:
        user_id = match.group(1)
        chat: Optional[Chat] = update.effective_chat
        res = sql.remove_warn(user_id, chat.id)
        
        if res:
            user_member = await chat.get_member(user_id)
            await update.effective_message.edit_text(
                f"✅ {mention_html(user_member.user.id, user_member.user.first_name)} [<code>{user_member.user.id}</code>] **Warn removed.**",
                parse_mode=ParseMode.HTML,
            )
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#UNWARN\n"
                f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                f"<b>User:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
            )
        else:
            await update.effective_message.edit_text(
                "ℹ️ **User already has no warns.**", parse_mode=ParseMode.HTML
            )

    return ""


@user_admin
@can_restrict
@loggable
async def warn_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    args = context.args
    message: Optional[Message] = update.effective_message
    chat: Optional[Chat] = update.effective_chat
    warner: Optional[User] = update.effective_user

    user_id, reason = extract_user_and_text(message, args)
    
    # Handle /dwarn (delete and warn)
    if message.text.startswith("/d") and message.reply_to_message:
        await message.reply_to_message.delete()
        
    if user_id:
        if (
            message.reply_to_message
            and message.reply_to_message.from_user.id == user_id
        ):
            return await warn(
                message.reply_to_message.from_user,
                chat,
                reason,
                message.reply_to_message,
                warner,
            )
        else:
            user_member = await chat.get_member(user_id)
            return await warn(user_member.user, chat, reason, message, warner)
    else:
        await message.reply_text("❌ **That looks like an invalid User ID to me.**")
    return ""


@user_admin
@bot_admin
@loggable
async def reset_warns(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    args = context.args
    message: Optional[Message] = update.effective_message
    chat: Optional[Chat] = update.effective_chat
    user: Optional[User] = update.effective_user

    user_id = extract_user(message, args)

    if user_id:
        sql.reset_warns(user_id, chat.id)
        await message.reply_text("✅ **Warns have been reset!**")
        warned_member = await chat.get_member(user_id)
        warned = warned_member.user
        return (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#RESETWARNS\n"
            f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
            f"<b>User:</b> {mention_html(warned.id, warned.first_name)}"
        )
    else:
        await message.reply_text("⚠️ **No user has been designated!**")
    return ""


async def warns(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    message: Optional[Message] = update.effective_message
    chat: Optional[Chat] = update.effective_chat
    user_id = extract_user(message, args) or update.effective_user.id
    result = sql.get_warns(user_id, chat.id)

    if result and result[0] != 0:
        num_warns, reasons = result
        limit, soft_warn = sql.get_warn_setting(chat.id)

        if reasons:
            text = (
                f"⚠️ **This user has {num_warns}/{limit} warns, for the following reasons:**"
            )
            for reason in reasons:
                text += f"\n • {reason}"

            msgs = split_message(text)
            for msg in msgs:
                await update.effective_message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
        else:
            await update.effective_message.reply_text(
                f"⚠️ **User has {num_warns}/{limit} warns, but no reasons for any of them.**"
            )
    else:
        await update.effective_message.reply_text("✅ **This user doesn't have any warns!**")

@user_admin
async def add_warn_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat: Optional[Chat] = update.effective_chat
    msg: Optional[Message] = update.effective_message

    args = msg.text.split(
        None, 1
    )  # use python's maxsplit to separate Cmd, keyword, and reply_text

    if len(args) < 2:
        await msg.reply_text("❌ **Please provide both keyword and warning message!**")
        return

    extracted = split_quotes(args[1])

    if len(extracted) >= 2:
        # set trigger -> lower, so as to avoid adding duplicate filters with different cases
        keyword = extracted[0].lower()
        content = extracted[1]
    else:
        await msg.reply_text("❌ **Please use quotes around your keyword and message!**\n**Example:** `/addwarn \"spam\" This is spam!`")
        return

    sql.add_warn_filter(chat.id, keyword, content)
    await update.effective_message.reply_text(f"✅ **Warn handler added for** `{keyword}`**!**")


@user_admin
async def remove_warn_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat: Optional[Chat] = update.effective_chat
    msg: Optional[Message] = update.effective_message

    args = msg.text.split(
        None, 1
    )  # use python's maxsplit to separate Cmd, keyword, and reply_text

    if len(args) < 2:
        await msg.reply_text("❌ **Please specify which warning filter to remove!**")
        return

    extracted = split_quotes(args[1])

    if len(extracted) < 1:
        await msg.reply_text("❌ **Please specify the keyword to remove!**")
        return

    to_remove = extracted[0]
    chat_filters = sql.get_chat_warn_triggers(chat.id)

    if not chat_filters:
        await msg.reply_text("❌ **No warning filters are active here!**")
        return

    for filt in chat_filters:
        if filt == to_remove:
            sql.remove_warn_filter(chat.id, to_remove)
            await msg.reply_text("✅ **Okay, I'll stop warning people for that.**")
            return

    await msg.reply_text(
        "❌ **That's not a current warning filter - run** `/warnlist` **for all active warning filters.**"
    )


async def list_warn_filters(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat: Optional[Chat] = update.effective_chat
    all_handlers = sql.get_chat_warn_triggers(chat.id)

    if not all_handlers:
        await update.effective_message.reply_text("❌ **No warning filters are active here!**")
        return

    filter_list = CURRENT_WARNING_FILTER_STRING
    for keyword in all_handlers:
        entry = f" • `{html.escape(keyword)}`\n"
        if len(entry) + len(filter_list) > telegram.MAX_MESSAGE_LENGTH:
            await update.effective_message.reply_text(filter_list, parse_mode=ParseMode.HTML)
            filter_list = entry
        else:
            filter_list += entry

    if filter_list != CURRENT_WARNING_FILTER_STRING:
        await update.effective_message.reply_text(filter_list, parse_mode=ParseMode.HTML)


@loggable
async def reply_filter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    chat: Optional[Chat] = update.effective_chat
    message: Optional[Message] = update.effective_message
    user: Optional[User] = update.effective_user

    if not user:  # Ignore channel
        return

    if user.id == 777000:  # Telegram service account
        return
        
    if is_approved(chat.id, user.id):
        return
        
    chat_warn_filters = sql.get_chat_warn_triggers(chat.id)
    to_match = extract_text(message)
    if not to_match:
        return ""

    for keyword in chat_warn_filters:
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, to_match, flags=re.IGNORECASE):
            user: Optional[User] = update.effective_user
            warn_filter = sql.get_warn_filter(chat.id, keyword)
            return await warn(user, chat, warn_filter.reply, message)
    return ""


@user_admin
@loggable
async def set_warn_limit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    args = context.args
    chat: Optional[Chat] = update.effective_chat
    user: Optional[User] = update.effective_user
    msg: Optional[Message] = update.effective_message

    if args:
        if args[0].isdigit():
            if int(args[0]) < 3:
                await msg.reply_text("❌ **The minimum warn limit is 3!**")
            else:
                sql.set_warn_limit(chat.id, int(args[0]))
                await msg.reply_text(f"✅ **Updated the warn limit to {args[0]}**")
                return (
                    f"<b>{html.escape(chat.title)}:</b>\n"
                    f"#SET_WARN_LIMIT\n"
                    f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                    f"Set the warn limit to <code>{args[0]}</code>"
                )
        else:
            await msg.reply_text("❌ **Give me a number as an argument!**")
    else:
        limit, soft_warn = sql.get_warn_setting(chat.id)
        await msg.reply_text(f"ℹ️ **The current warn limit is {limit}**")
    return ""


@user_admin
@loggable
async def set_warn_strength(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    args = context.args
    chat: Optional[Chat] = update.effective_chat
    user: Optional[User] = update.effective_user
    msg: Optional[Message] = update.effective_message

    if args:
        if args[0].lower() in ("on", "yes"):
            sql.set_warn_strength(chat.id, False)
            await msg.reply_text("🔨 **Too many warns will now result in a Ban!**")
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#SET_WARN_STRENGTH\n"
                f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                f"Has enabled strong warns. Users will be banned."
            )

        elif args[0].lower() in ("off", "no"):
            sql.set_warn_strength(chat.id, True)
            await msg.reply_text(
                "👢 **Too many warns will now result in a kick!** Users will be able to join again after."
            )
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#SET_WARN_STRENGTH\n"
                f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                f"Has disabled strong warns. Users will be kicked."
            )

        else:
            await msg.reply_text("❌ **I only understand on/yes/no/off!**")
    else:
        limit, soft_warn = sql.get_warn_setting(chat.id)
        if soft_warn:
            await msg.reply_text(
                "👢 **Warns are currently set to** *kick* **users when they exceed the limits.**",
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            await msg.reply_text(
                "🔨 **Warns are currently set to** *ban* **users when they exceed the limits.**",
                parse_mode=ParseMode.MARKDOWN,
            )
    return ""


def __stats__():
    return (
        f"× {sql.num_warns()} overall warns, across {sql.num_warn_chats()} chats.\n"
        f"× {sql.num_warn_filters()} warn filters, across {sql.num_warn_filter_chats()} chats."
    )


def __import_data__(chat_id, data):
    for user_id, count in data.get("warns", {}).items():
        for x in range(int(count)):
            sql.warn_user(user_id, chat_id)


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    num_warn_filters = sql.num_warn_chat_filters(chat_id)
    limit, soft_warn = sql.get_warn_setting(chat_id)
    return (
        f"This chat has `{num_warn_filters}` warn filters. "
        f"It takes `{limit}` warns before the user gets *{'kicked' if soft_warn else 'banned'}*."
    )


__help__ = """
*Warning System - Keep Your Chat Clean*

**User Commands:**
❂ `/warns <user>` - Get a user's number and reason of warns

**Admin Commands:**
❂ `/warn <user> [reason]` - Warn a user (reply or mention)
❂ `/dwarn <user> [reason]` - Warn a user and delete the message
❂ `/resetwarn <user>` - Reset warns for a user
❂ `/warnlimit <number>` - Set the warning limit (minimum 3)
❂ `/strongwarn <on/off>` - Toggle ban/kick on warn limit

**Warning Filters:**
❂ `/addwarn <"keyword"> <message>` - Add automatic warning filter
❂ `/nowarn <"keyword">` - Remove warning filter
❂ `/warnlist` - List all warning filters in chat

**Settings:**
• Default warn limit: 3 warnings
• After reaching limit: kick (soft) or ban (strong)
• Warning filters automatically warn users for specific words
• Approved users and elevated users are immune
• Admins cannot be warned

**Examples:**
• `/warn @user Spamming` - Warn user for spamming
• `/addwarn "spam" Stop spamming!` - Auto-warn for "spam"
• `/warnlimit 5` - Set warn limit to 5
• `/strongwarn on` - Enable bans instead of kicks

**Features:**
• Interactive warn removal buttons for admins
• Comprehensive logging system
• Import/export support for chat migration
• Statistics tracking across all chats
"""

__mod_name__ = "Warning ⚠"

WARN_HANDLER = CommandHandler(
    ["warn", "dwarn"], warn_user, filters=filters.ChatType.GROUPS
)
RESET_WARN_HANDLER = CommandHandler(
    ["resetwarn", "resetwarns"],
    reset_warns,
    filters=filters.ChatType.GROUPS,
)
CALLBACK_QUERY_HANDLER = CallbackQueryHandler(
    button, pattern=r"rm_warn"
)
MYWARNS_HANDLER = DisableAbleCommandHandler(
    "warns", warns, filters=filters.ChatType.GROUPS
)
ADD_WARN_HANDLER = CommandHandler(
    "addwarn", add_warn_filter, filters=filters.ChatType.GROUPS
)
RM_WARN_HANDLER = CommandHandler(
    ["nowarn", "stopwarn"],
    remove_warn_filter,
    filters=filters.ChatType.GROUPS,
)
LIST_WARN_HANDLER = DisableAbleCommandHandler(
    ["warnlist", "warnfilters"],
    list_warn_filters,
    filters=filters.ChatType.GROUPS,
    admin_ok=True,
)
WARN_FILTER_HANDLER = MessageHandler(
    CustomFilters.has_text & filters.ChatType.GROUPS, reply_filter
)
WARN_LIMIT_HANDLER = CommandHandler(
    "warnlimit", set_warn_limit, filters=filters.ChatType.GROUPS
)
WARN_STRENGTH_HANDLER = CommandHandler(
    "strongwarn", set_warn_strength, filters=filters.ChatType.GROUPS
)

application.add_handler(WARN_HANDLER)
application.add_handler(CALLBACK_QUERY_HANDLER)
application.add_handler(RESET_WARN_HANDLER)
application.add_handler(MYWARNS_HANDLER)
application.add_handler(ADD_WARN_HANDLER)
application.add_handler(RM_WARN_HANDLER)
application.add_handler(LIST_WARN_HANDLER)
application.add_handler(WARN_LIMIT_HANDLER)
application.add_handler(WARN_STRENGTH_HANDLER)
application.add_handler(WARN_FILTER_HANDLER, WARN_HANDLER_GROUP)
