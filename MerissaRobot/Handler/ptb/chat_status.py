from functools import wraps
from threading import RLock
from time import perf_counter
from typing import Optional, Callable, Any, Coroutine

from cachetools import TTLCache
from telegram import Chat, ChatMember, Update, Message
from telegram.constants import ParseMode, ChatMemberStatus
from telegram.ext import ContextTypes

from MerissaRobot import (
    DEL_CMDS,
    DEMONS,
    DEV_USERS,
    DRAGONS,
    SUPPORT_CHAT,
    TIGERS,
    WOLVES,
    application,  # Changed from dispatcher
)

# stores admins in memory for 10 min.
ADMIN_CACHE = TTLCache(maxsize=512, ttl=60 * 10, timer=perf_counter)
THREAD_LOCK = RLock()

# ───────────────────────────────
# Simple ID-list privilege checks
# ───────────────────────────────

def is_whitelist_plus_local(user_id: int) -> bool:
    return any(user_id in group for group in [WOLVES, TIGERS, DEMONS, DRAGONS, DEV_USERS])

def is_support_plus_local(user_id: int) -> bool:
    return user_id in DEMONS or user_id in DRAGONS or user_id in DEV_USERS

def is_sudo_plus_local(user_id: int) -> bool:
    return user_id in DRAGONS or user_id in DEV_USERS


# ───────────────────────────────
# Telegram API dependent checks (async)
# ───────────────────────────────

async def is_user_admin(chat: Chat, user_id: int, member: Optional[ChatMember] = None) -> bool:
    if (
        chat.type == "private"
        or user_id in DRAGONS
        or user_id in DEV_USERS
        or user_id in [777000, 1087968824]  # Telegram & Anonymous Admin
    ):
        return True

    if member is None:
        with THREAD_LOCK:
            try:
                return user_id in ADMIN_CACHE[chat.id]
            except KeyError:
                # refresh cache
                chat_admins = await application.bot.get_chat_administrators(chat.id)  # Changed from dispatcher
                admin_list = [x.user.id for x in chat_admins]
                ADMIN_CACHE[chat.id] = admin_list
                return user_id in admin_list
    else:
        return member.status in {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}


async def is_bot_admin(chat: Chat, bot_id: int, bot_member: Optional[ChatMember] = None) -> bool:
    if chat.type == "private":
        return True

    if bot_member is None:
        bot_member = await chat.get_member(bot_id)

    return bot_member.status in {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}


async def can_delete(chat: Chat, bot_id: int) -> bool:
    member = await chat.get_member(bot_id)
    return getattr(member, "can_delete_messages", False)


async def is_user_ban_protected(chat: Chat, user_id: int, member: Optional[ChatMember] = None) -> bool:
    if (
        chat.type == "private"
        or user_id in DRAGONS
        or user_id in DEV_USERS
        or user_id in WOLVES
        or user_id in TIGERS
        or user_id in [777000, 1087968824]  # Telegram & Anonymous Admin
    ):
        return True

    if member is None:
        member = await chat.get_member(user_id)

    return member.status in {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}


async def is_user_in_chat(chat: Chat, user_id: int) -> bool:
    member = await chat.get_member(user_id)
    return member.status not in {ChatMemberStatus.LEFT, ChatMemberStatus.BANNED}


# ───────────────────────────────
# Decorator helpers (async wrappers)
# ───────────────────────────────

Decorator = Callable[..., Callable[..., Coroutine[Any, Any, Any]]]

def dev_plus(func):
    @wraps(func)
    async def is_dev_plus_func(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        if user and user.id in DEV_USERS:
            return await func(update, context, *args, **kwargs)

        if not user:
            return

        if DEL_CMDS and (update.effective_message and update.effective_message.text and " " not in update.effective_message.text):
            try:
                await update.effective_message.delete()
            except Exception:
                pass
        else:
            await update.effective_message.reply_text(
                "This is a developer restricted command. You do not have permissions to run this."
            )
    return is_dev_plus_func


def sudo_plus(func):
    @wraps(func)
    async def is_sudo_plus_func(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        if user and is_sudo_plus_local(user.id):
            return await func(update, context, *args, **kwargs)

        if not user:
            return

        if DEL_CMDS and (update.effective_message and update.effective_message.text and " " not in update.effective_message.text):
            try:
                await update.effective_message.delete()
            except Exception:
                pass
        else:
            await update.effective_message.reply_text(
                "Who dis non-admin telling me what to do? You want a punch?",
            )
    return is_sudo_plus_func


def support_plus(func):
    @wraps(func)
    async def is_support_plus_func(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        if user and is_support_plus_local(user.id):
            return await func(update, context, *args, **kwargs)

        if DEL_CMDS and (update.effective_message and update.effective_message.text and " " not in update.effective_message.text):
            try:
                await update.effective_message.delete()
            except Exception:
                pass
    return is_support_plus_func


def whitelist_plus(func):
    @wraps(func)
    async def is_whitelist_plus_func(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        if user and is_whitelist_plus_local(user.id):
            return await func(update, context, *args, **kwargs)

        await update.effective_message.reply_text(
            f"You don't have access to use this.\nVisit @{SUPPORT_CHAT}",
        )
    return is_whitelist_plus_func


def user_admin(func):
    @wraps(func)
    async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        chat = update.effective_chat

        if user and await is_user_admin(chat, user.id):
            return await func(update, context, *args, **kwargs)

        if not user:
            return

        if DEL_CMDS and (update.effective_message and update.effective_message.text and " " not in update.effective_message.text):
            try:
                await update.effective_message.delete()
            except Exception:
                pass
        else:
            await update.effective_message.reply_text(
                "Who dis non-admin telling me what to do? You want a punch?",
            )
    return is_admin


def cuser_admin(func):
    @wraps(func)
    async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        query = update.callback_query
        user = update.effective_user
        chat = update.effective_chat

        if user and await is_user_admin(chat, user.id):
            return await func(update, context, *args, **kwargs)

        if not user:
            return

        if DEL_CMDS and update.effective_message and update.effective_message.text and " " not in update.effective_message.text:
            try:
                await update.effective_message.delete()
            except Exception:
                pass
        else:
            if query:
                await query.answer("Who dis non-admin telling me what to do? You want a punch?")
    return is_admin


def user_admin_no_reply(func):
    @wraps(func)
    async def is_not_admin_no_reply(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        chat = update.effective_chat

        if user and await is_user_admin(chat, user.id):
            return await func(update, context, *args, **kwargs)

        if not user:
            return

        if DEL_CMDS and (update.effective_message and update.effective_message.text and " " not in update.effective_message.text):
            try:
                await update.effective_message.delete()
            except Exception:
                pass
    return is_not_admin_no_reply


def user_not_admin(func):
    @wraps(func)
    async def is_not_admin(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        chat = update.effective_chat

        if user and not (await is_user_admin(chat, user.id)):
            return await func(update, context, *args, **kwargs)
    return is_not_admin


def bot_admin(func):
    @wraps(func)
    async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        bot = context.bot
        chat = update.effective_chat
        update_chat_title = chat.title
        message_chat_title = update.effective_message.chat.title

        not_admin = "I'm not admin!" if update_chat_title == message_chat_title else f"I'm not admin in <b>{update_chat_title}</b>!"
        if await is_bot_admin(chat, bot.id):
            return await func(update, context, *args, **kwargs)

        await update.effective_message.reply_text(not_admin, parse_mode=ParseMode.HTML)
    return is_admin


def bot_can_delete(func):
    @wraps(func)
    async def delete_rights(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        bot = context.bot
        chat = update.effective_chat
        update_chat_title = chat.title
        message_chat_title = update.effective_message.chat.title

        cant_delete = (
            "I can't delete messages here!\nMake sure I'm admin and can delete other user's messages."
            if update_chat_title == message_chat_title
            else f"I can't delete messages in <b>{update_chat_title}</b>!\nMake sure I'm admin and can delete other user's messages there."
        )

        if await can_delete(chat, bot.id):
            return await func(update, context, *args, **kwargs)

        await update.effective_message.reply_text(cant_delete, parse_mode=ParseMode.HTML)
    return delete_rights


def can_pin(func):
    @wraps(func)
    async def pin_rights(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        bot = context.bot
        chat = update.effective_chat
        update_chat_title = chat.title
        message_chat_title = update.effective_message.chat.title

        cant_pin = (
            "I can't pin messages here!\nMake sure I'm admin and can pin messages."
            if update_chat_title == message_chat_title
            else f"I can't pin messages in <b>{update_chat_title}</b>!\nMake sure I'm admin and can pin messages there."
        )

        member = await chat.get_member(bot.id)
        if getattr(member, "can_pin_messages", False):
            return await func(update, context, *args, **kwargs)

        await update.effective_message.reply_text(cant_pin, parse_mode=ParseMode.HTML)
    return pin_rights


def can_promote(func):
    @wraps(func)
    async def promote_rights(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        bot = context.bot
        chat = update.effective_chat
        update_chat_title = chat.title
        message_chat_title = update.effective_message.chat.title

        cant_promote = (
            "I can't promote/demote people here!\nMake sure I'm admin and can appoint new admins."
            if update_chat_title == message_chat_title
            else f"I can't promote/demote people in <b>{update_chat_title}</b>!\nMake sure I'm admin there and can appoint new admins."
        )

        member = await chat.get_member(bot.id)
        if getattr(member, "can_promote_members", False):
            return await func(update, context, *args, **kwargs)

        await update.effective_message.reply_text(cant_promote, parse_mode=ParseMode.HTML)
    return promote_rights


def can_restrict(func):
    @wraps(func)
    async def restrict_rights(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        bot = context.bot
        chat = update.effective_chat
        update_chat_title = chat.title
        message_chat_title = update.effective_message.chat.title

        cant_restrict = (
            "I can't restrict people here!\nMake sure I'm admin and can restrict users."
            if update_chat_title == message_chat_title
            else f"I can't restrict people in <b>{update_chat_title}</b>!\nMake sure I'm admin there and can restrict users."
        )

        member = await chat.get_member(bot.id)
        if getattr(member, "can_restrict_members", False):
            return await func(update, context, *args, **kwargs)

        await update.effective_message.reply_text(cant_restrict, parse_mode=ParseMode.HTML)
    return restrict_rights


def user_can_ban(func):
    @wraps(func)
    async def user_is_banhammer(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        member = await update.effective_chat.get_member(user_id)

        if (
            not (getattr(member, "can_restrict_members", False) or member.status == ChatMemberStatus.OWNER)
            and user_id not in DRAGONS
            and user_id not in [777000, 1087968824]
        ):
            await update.effective_message.reply_text(
                "Sorry son, but you're not worthy to wield the banhammer.",
            )
            return ""
        return await func(update, context, *args, **kwargs)
    return user_is_banhammer


def connection_status(func):
    @wraps(func)
    async def connected_status(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        # connected(...) is imported below
        conn = connected(
            context.bot,
            update,
            update.effective_chat,
            update.effective_user.id,
            need_admin=False,
        )

        if conn:
            chat = await application.bot.get_chat(conn)  # Changed from dispatcher
            setattr(update, "_effective_chat", chat)
            return await func(update, context, *args, **kwargs)

        if update.effective_message.chat.type == "private":
            await update.effective_message.reply_text(
                "Send /connect in a group that you and I have in common first.",
            )
            return connected_status

        return await func(update, context, *args, **kwargs)
    return connected_status


# Workaround for circular import with connection.py
from MerissaRobot.Modules import connection
connected = connection.connected
