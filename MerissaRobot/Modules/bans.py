import html
from typing import Optional

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    TelegramError,
    Update,
)
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.ext import ContextTypes, CallbackQueryHandler, CommandHandler, filters
from telegram.helpers import mention_html

from MerissaRobot import (
    DEMONS,
    DEV_USERS,
    DRAGONS,
    LOGGER,
    OWNER_ID,
    TIGERS,
    WOLVES,
    application,
)
from MerissaRobot.Handler.ptb.chat_status import (
    bot_admin,
    can_delete,
    can_restrict,
    connection_status,
    dev_plus,
    is_user_admin,
    is_user_ban_protected,
    is_user_in_chat,
    user_admin,
    user_admin_no_reply,
    user_can_ban,
)
from MerissaRobot.Handler.ptb.extraction import extract_user_and_text
from MerissaRobot.Handler.ptb.filters import CustomFilters
from MerissaRobot.Handler.ptb.string_handling import extract_time
from MerissaRobot.Modules.disable import DisableAbleCommandHandler
from MerissaRobot.Modules.log_channel import gloggable, loggable


@connection_status
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    log_message = ""
    bot = context.bot
    args = context.args
    reason = ""
    
    if message.reply_to_message and message.reply_to_message.sender_chat:
        r = await bot.ban_chat_sender_chat(
            chat_id=chat.id, sender_chat_id=message.reply_to_message.sender_chat.id
        )
        if r:
            await message.reply_text(
                "Channel {} was banned successfully from {}".format(
                    html.escape(message.reply_to_message.sender_chat.title),
                    html.escape(chat.title),
                ),
                parse_mode="html",
            )
        else:
            await message.reply_text("Failed to ban channel")
        return

    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        await message.reply_text("⚠️ User not found.")
        return log_message
    try:
        member = await chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "User not found":
            raise
        await message.reply_text("Can't seem to find this person.")
        return log_message
    if user_id == bot.id:
        await message.reply_text("Oh yeah, ban myself, noob!")
        return log_message

    if is_user_ban_protected(chat, user_id, member) and user not in DEV_USERS:
        if user_id == OWNER_ID:
            await message.reply_text("Trying to put me against a King huh?")
        elif user_id in DEV_USERS:
            await message.reply_text("I can't act against our Prince.")
        elif user_id in DRAGONS:
            await message.reply_text(
                "Fighting this Emperor here will put user lives at risk."
            )
        elif user_id in DEMONS:
            await message.reply_text(
                "Bring an order from Captain to fight a Assasin servant."
            )
        elif user_id in TIGERS:
            await message.reply_text("Bring an order from Soldier to fight a Lancer servant.")
        elif user_id in WOLVES:
            await message.reply_text("Trader access make them ban immune!")
        else:
            await message.reply_text("⚠️ Cannot banned admin.")
        return log_message
        
    if message.text.startswith("/s"):
        silent = True
        if not can_delete(chat, context.bot.id):
            return ""
    else:
        silent = False
        
    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#{'S' if silent else ''}BANNED\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>User:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
    )
    if reason:
        log += f"<b>Reason:</b> {reason}"

    try:
        await chat.ban_member(user_id)

        if silent:
            if message.reply_to_message:
                await message.reply_to_message.delete()
            await message.delete()
            return log

        reply = f"{mention_html(member.user.id, html.escape(member.user.first_name))} [<code>{member.user.id}</code>] Banned."
        if reason:
            reply += f"\nReason: {html.escape(reason)}"

        await bot.send_message(
            chat.id,
            reply,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="🔄  Unban", callback_data=f"unbanb_unban={user_id}"
                        ),
                        InlineKeyboardButton(
                            text="🗑️  Delete", callback_data="unbanb_del"
                        ),
                    ]
                ]
            ),
            parse_mode=ParseMode.HTML,
        )
        return log

    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            if silent:
                return log
            await message.reply_text("Banned!", quote=False)
            return log
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "ERROR banning user %s in chat %s (%s) due to %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            await message.reply_text("Uhm...that didn't work...")

    return log_message


@connection_status
@bot_admin
@can_restrict
@user_admin
@loggable
async def dban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    args = context.args
    bot = context.bot

    if message.reply_to_message:
        user = update.effective_user
        chat = update.effective_chat
        if can_delete(chat, bot.id):
            await update.effective_message.reply_to_message.delete()
    else:
        await message.reply_text(
            "You have to reply to a message to delete it and ban the user."
        )
        return ""

    user_id, reason = extract_user_and_text(message, args)

    try:
        member = await chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            await message.reply_text("I can't seem to find this user")
            return ""
        else:
            raise

    if is_user_ban_protected(chat, user_id, member):
        await message.reply_text("I'm not gonna ban an admin, don't make fun of yourself!")
        return ""

    if user_id == context.bot.id:
        await message.reply_text("I'm not gonna ban myself, that's pretty dumb idea!")
        return ""

    if user_id == 777000 or user_id == 1087968824:
        await message.reply_text(
            str(user_id) + " is an account reserved for telegram, I cannot ban it!"
        )
        return ""

    log = (
        f"<b>{html.escape(chat.title)}:</b>"
        f"\n#BANNED"
        f"\n<b>Admin:</b> {mention_html(user.id, user.first_name)}"
        f"\n<b>User:</b> {mention_html(member.user.id, member.user.first_name)} (<code>{member.user.id}</code>)"
    )
    if reason:
        log += f"\n<b>Reason:</b> {reason}"

    try:
        await chat.ban_member(user_id)
        await context.bot.send_message(
            chat.id,
            "Admin {} has successfully banned {} in <b>{}</b>!.".format(
                mention_html(user.id, user.first_name),
                mention_html(member.user.id, member.user.first_name),
                html.escape(chat.title),
            ),
            parse_mode=ParseMode.HTML,
        )
        return log

    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            await message.reply_text("Banned!", quote=False)
            return log
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "ERROR banning user %s in chat %s (%s) due to %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            await message.reply_text("Well damn, I can't ban that user.")

    return ""


@connection_status
@bot_admin
@can_restrict
@user_admin
@loggable
async def dkick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    args = context.args
    bot = context.bot

    if message.reply_to_message:
        user = update.effective_user
        chat = update.effective_chat
        if can_delete(chat, bot.id):
            await update.effective_message.reply_to_message.delete()
    else:
        await message.reply_text(
            "You have to reply to a message to delete it and kick the user."
        )
        return ""

    user_id, reason = extract_user_and_text(message, args)

    try:
        member = await chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            await message.reply_text("I can't seem to find this user")
            return ""
        else:
            raise

    if is_user_ban_protected(chat, user_id):
        await message.reply_text("Yeahh... let's start kicking admins?")
        return ""

    if user_id == context.bot.id:
        await message.reply_text("Yeahhh I'm not gonna do that")
        return ""

    if user_id == 777000 or user_id == 1087968824:
        await message.reply_text(
            str(user_id) + " is an account reserved for telegram, I cannot kick it!"
        )
        return ""

    res = await chat.unban_member(user_id)  # unban on current user = kick
    if res:
        await context.bot.send_message(
            chat.id,
            "Admin {} has successfully kicked {} in <b>{}</b>!".format(
                mention_html(user.id, user.first_name),
                mention_html(member.user.id, member.user.first_name),
                html.escape(chat.title),
            ),
            parse_mode=ParseMode.HTML,
        )
        log = (
            f"<b>{html.escape(chat.title)}:</b>"
            f"\n#KICKED"
            f"\n<b>Admin:</b> {mention_html(user.id, user.first_name)}"
            f"\n<b>User:</b> {mention_html(member.user.id, member.user.first_name)} (<code>{member.user.id}</code>)"
        )
        if reason:
            log += f"\n<b>Reason:</b> {reason}"

        return log

    else:
        await message.reply_text("Get Out!.")

    return ""

@connection_status
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
async def temp_ban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    log_message = ""
    bot, args = context.bot, context.args
    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        await message.reply_text("⚠️ User not found.")
        return log_message

    try:
        member = await chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "User not found":
            raise
        await message.reply_text("I can't seem to find this user.")
        return log_message
    if user_id == bot.id:
        await message.reply_text("I'm not gonna BAN myself, are you crazy?")
        return log_message

    if is_user_ban_protected(chat, user_id, member):
        await message.reply_text("I don't feel like it.")
        return log_message

    if not reason:
        await message.reply_text("You haven't specified a time to ban this user for!")
        return log_message

    split_reason = reason.split(None, 1)

    time_val = split_reason[0].lower()
    reason = split_reason[1] if len(split_reason) > 1 else ""
    bantime = extract_time(message, time_val)

    if not bantime:
        return log_message

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        "#TEMP BANNED\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>User:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}\n"
        f"<b>Time:</b> {time_val}"
    )
    if reason:
        log += f"\nReason: {reason}"

    try:
        await chat.ban_member(user_id, until_date=bantime)

        reply_msg = (
            f"{mention_html(member.user.id, html.escape(member.user.first_name))} [<code>{member.user.id}</code>] Temporary Banned"
            f" for (`{time_val}`)."
        )

        if reason:
            reply_msg += f"\nReason: `{html.escape(reason)}`"

        await bot.send_message(
            chat.id,
            reply_msg,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="🔄  Unban", callback_data=f"unbanb_unban={user_id}"
                        ),
                        InlineKeyboardButton(
                            text="🗑️  Delete", callback_data="unbanb_del"
                        ),
                    ]
                ]
            ),
            parse_mode=ParseMode.HTML,
        )
        return log

    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            await message.reply_text(
                f"{mention_html(member.user.id, html.escape(member.user.first_name))} [<code>{member.user.id}</code>] banned for {time_val}.",
                quote=False,
            )
            return log
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "ERROR banning user %s in chat %s (%s) due to %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            await message.reply_text("Well damn, I can't ban that user.")

    return log_message


@connection_status
@bot_admin
@can_restrict
@user_admin_no_reply
@user_can_ban
@loggable
async def unbanb_btn(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    bot = context.bot
    query = update.callback_query
    chat = update.effective_chat
    user = update.effective_user
    
    if query.data != "unbanb_del":
        splitter = query.data.split("=")
        query_match = splitter[0]
        if query_match == "unbanb_unban":
            user_id = splitter[1]
            if not is_user_admin(chat, int(user.id)):
                await bot.answer_callback_query(
                    query.id,
                    text="⚠️ You don't have enough rights to unmute people",
                    show_alert=True,
                )
                return ""
            try:
                member = await chat.get_member(user_id)
            except BadRequest:
                pass
            await chat.unban_member(user_id)
            await query.message.edit_text(
                f"{member.user.first_name} [{member.user.id}] Unbanned."
            )
            await bot.answer_callback_query(query.id, text="Unbanned!")
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#UNBANNED\n"
                f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}"
            )

    else:
        if not is_user_admin(chat, int(user.id)):
            await bot.answer_callback_query(
                query.id,
                text="⚠️ You don't have enough rights to delete this message.",
                show_alert=True,
            )
            return ""
        await query.message.delete()
        await bot.answer_callback_query(query.id, text="Deleted!")
        return ""


@connection_status
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
async def punch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    log_message = ""
    bot, args = context.bot, context.args
    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        await message.reply_text("⚠️ User not found")
        return log_message

    try:
        member = await chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "User not found":
            raise

        await message.reply_text("⚠️ I can't seem to find this user.")
        return log_message
    if user_id == bot.id:
        await message.reply_text("Yeahhh I'm not gonna do that.")
        return log_message

    if is_user_ban_protected(chat, user_id):
        await message.reply_text("I really wish I could punch this user....")
        return log_message

    res = await chat.unban_member(user_id)  # unban on current user = kick
    if res:
        await bot.send_message(
            chat.id,
            f"{mention_html(member.user.id, html.escape(member.user.first_name))} [<code>{member.user.id}</code>] Kicked.",
            parse_mode=ParseMode.HTML,
        )
        log = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#KICKED\n"
            f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            f"<b>User:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
        )
        if reason:
            log += f"\n<b>Reason:</b> {reason}"

        return log

    else:
        await message.reply_text("⚠️ Well damn, I can't punch that user.")

    return log_message


@bot_admin
@can_restrict
async def punchme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_message.from_user.id
    if is_user_admin(update.effective_chat, user_id):
        await update.effective_message.reply_text("I wish I could... but you're an admin.")
        return

    res = await update.effective_chat.unban_member(user_id)  # unban on current user = kick
    if res:
        await update.effective_message.reply_text(
            "punches you out of the group!!",
        )
    else:
        await update.effective_message.reply_text("Huh? I can't :/")


@connection_status
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    log_message = ""
    bot, args = context.bot, context.args
    
    if message.reply_to_message and message.reply_to_message.sender_chat:
        r = await bot.unban_chat_sender_chat(
            chat_id=chat.id, sender_chat_id=message.reply_to_message.sender_chat.id
        )
        if r:
            await message.reply_text(
                "Channel {} was unbanned successfully from {}".format(
                    html.escape(message.reply_to_message.sender_chat.title),
                    html.escape(chat.title),
                ),
                parse_mode="html",
            )
        else:
            await message.reply_text("Failed to unban channel")
        return

    user_id, reason = extract_user_and_text(message, args)
    if not user_id:
        await message.reply_text("⚠️ User not found.")
        return log_message

    try:
        member = await chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "User not found":
            raise
        await message.reply_text("I can't seem to find this user.")
        return log_message
    if user_id == bot.id:
        await message.reply_text("How would I unban myself if I wasn't here...?")
        return log_message

    if is_user_in_chat(chat, user_id):
        await message.reply_text(f"⚠️ User not found.")
        return log_message

    await chat.unban_member(user_id)
    await message.reply_text(f"{member.user.first_name} [{member.user.id}] Unbanned.")

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#UNBANNED\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>User:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
    )
    if reason:
        log += f"\n<b>Reason:</b> {reason}"

    return log


@connection_status
@bot_admin
@can_restrict
@gloggable
async def selfunban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    message = update.effective_message
    user = update.effective_user
    bot, args = context.bot, context.args
    
    if user.id not in DRAGONS and user.id not in TIGERS:
        return

    try:
        chat_id = int(args[0])
    except:
        await message.reply_text("Give a valid chat ID.")
        return

    chat = await bot.get_chat(chat_id)

    try:
        member = await chat.get_member(user.id)
    except BadRequest as excp:
        if excp.message == "User not found":
            await message.reply_text("I can't seem to find this user.")
            return
        else:
            raise

    if is_user_in_chat(chat, user.id):
        await message.reply_text("Aren't you already in the chat??")
        return

    await chat.unban_member(user.id)
    await message.reply_text(f"Yep, I have unbanned The user.")

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#UNBANNED\n"
        f"<b>User:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
    )

    return log


@bot_admin
@can_restrict
@loggable
async def banme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_message.from_user.id
    chat = update.effective_chat
    user = update.effective_user
    
    if is_user_admin(update.effective_chat, user_id):
        await update.effective_message.reply_text("⚠️ I cannot banned admin.")
        return

    res = await update.effective_chat.ban_member(user_id)
    if res:
        await update.effective_message.reply_text("Yes, you're right! GTFO..")
        return (
            f"<b>{html.escape(chat.title)}:</b>"
            f"\n#BANME"
            f"\n<b>User:</b> {mention_html(user.id, user.first_name)}"
            f"\n<b>ID:</b> <code>{user_id}</code>"
        )

    else:
        await update.effective_message.reply_text("Huh? I can't :/")


@dev_plus
async def snipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    bot = context.bot
    try:
        chat_id = str(args[0])
        del args[0]
    except TypeError:
        await update.effective_message.reply_text("Please give me a chat to echo to!")
    to_send = " ".join(args)
    if len(to_send) >= 2:
        try:
            await bot.send_message(int(chat_id), str(to_send))
        except TelegramError:
            LOGGER.warning("Couldn't send to group %s", str(chat_id))
            await update.effective_message.reply_text(
                "Couldn't send the message. Perhaps I'm not part of that group?"
            )


__help__ = """
*User Commands:*

❂ /kickme*:* kicks the user who issued the command

*Admins only:*

❂ /ban <userhandle>*:* bans a user. (via handle, or reply)
❂ /sban <userhandle>*:* Silently ban a user. Deletes command, Replied message and doesn't reply. (via handle, or reply)
❂ /tban <userhandle> x(m/h/d)*:* bans a user for x time. (via handle, or reply). m = minutes, h = hours, d = days.
❂ /unban <userhandle>*:* unbans a user. (via handle, or reply)
❂ /kick <userhandle>*:* kicks a user out of the group, (via handle, or reply)
❂ /mute <userhandle>*:* silences a user. Can also be used as a reply, muting the replied to user.
❂ /tmute <userhandle> x(m/h/d)*:* mutes a user for x time. (via handle, or reply). m = minutes, h = hours, d = days.
❂ /unmute <userhandle>*:* unmutes a user. Can also be used as a reply, muting the replied to user.
❂ /zombies*:* searches deleted accounts
❂ /zombies clean*:* removes deleted accounts from the group.
❂ /snipe <chatid> <string>*:* Make me send a message to a specific chat.
"""


__mod_name__ = "Bans 🚫"

BAN_HANDLER = CommandHandler(["ban", "sban"], ban)
TEMPBAN_HANDLER = CommandHandler(["tban"], temp_ban)
KICK_HANDLER = CommandHandler(["kick", "punch"], punch)
UNBAN_HANDLER = CommandHandler("unban", unban)
ROAR_HANDLER = CommandHandler("roar", selfunban)
UNBAN_BUTTON_HANDLER = CallbackQueryHandler(unbanb_btn, pattern=r"unbanb_")
KICKME_HANDLER = DisableAbleCommandHandler(
    ["kickme", "punchme"], punchme, filters=filters.ChatType.GROUPS
)
SNIPE_HANDLER = CommandHandler(
    "snipe", snipe, filters=CustomFilters.sudo_filter
)
BANME_HANDLER = CommandHandler("banme", banme)
DBAN_HANDLER = CommandHandler("dban", dban)
DKICK_HANDLER = CommandHandler("dkick", dkick)

application.add_handler(BAN_HANDLER)
application.add_handler(TEMPBAN_HANDLER)
application.add_handler(KICK_HANDLER)
application.add_handler(UNBAN_HANDLER)
application.add_handler(ROAR_HANDLER)
application.add_handler(KICKME_HANDLER)
application.add_handler(UNBAN_BUTTON_HANDLER)
application.add_handler(SNIPE_HANDLER)
application.add_handler(BANME_HANDLER)
application.add_handler(DBAN_HANDLER)
application.add_handler(DKICK_HANDLER)

__handlers__ = [
    BAN_HANDLER,
    TEMPBAN_HANDLER,
    KICK_HANDLER,
    UNBAN_HANDLER,
    ROAR_HANDLER,
    KICKME_HANDLER,
    UNBAN_BUTTON_HANDLER,
    SNIPE_HANDLER,
    BANME_HANDLER,
    DBAN_HANDLER,
    DKICK_HANDLER,
]
