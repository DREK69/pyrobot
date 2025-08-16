import functools
from enum import Enum
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, Message, User, Chat
from telegram.ext import ContextTypes
from telegram.constants import ParseMode, ChatMemberStatus
from telegram.error import BadRequest

from MerissaRobot import DEV_USERS, DRAGONS, dispatcher
from MerissaRobot.Handler.ptb.decorators import merissacallback


class AdminPerms(Enum):
    CAN_RESTRICT_MEMBERS = "can_restrict_members"
    CAN_PROMOTE_MEMBERS = "can_promote_members"
    CAN_INVITE_USERS = "can_invite_users"
    CAN_DELETE_MESSAGES = "can_delete_messages"
    CAN_CHANGE_INFO = "can_change_info"
    CAN_PIN_MESSAGES = "can_pin_messages"


class ChatStatus(Enum):
    CREATOR = ChatMemberStatus.OWNER        # ✅ use PTB v22 constants
    ADMIN = ChatMemberStatus.ADMINISTRATOR


anon_callbacks = {}
anon_callback_messages = {}
anon_users = {}


def user_admin(permission: AdminPerms):
    """Decorator to ensure the user has the required admin permission."""

    def wrapper(func):
        @functools.wraps(func)
        async def awrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            chat = update.effective_chat
            message: Message = update.effective_message

            # private chat → skip check
            if chat.type == "private":
                return await func(update, context, *args, **kwargs)

            is_anon = message.sender_chat
            if is_anon:
                # Anonymous admin → request verification via button
                callback_id = f"anoncb/{chat.id}/{message.message_id}/{permission.value}"
                anon_callbacks[(chat.id, message.message_id)] = ((update, context), func)

                sent_msg = await message.reply_text(
                    "Seems like you're anonymous, click the button below to prove your identity",
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="Prove identity", callback_data=callback_id)]]
                    ),
                )
                anon_callback_messages[(chat.id, message.message_id)] = sent_msg.message_id

            else:
                user_id = message.from_user.id
                mem = await context.bot.get_chat_member(chat_id=chat.id, user_id=user_id)

                if (
                    getattr(mem, permission.value, False)
                    or mem.status == ChatMemberStatus.OWNER
                    or user_id in DRAGONS
                ):
                    return await func(update, context, *args, **kwargs)
                else:
                    return await message.reply_text(
                        f"You lack the permission: `{permission.name}`",
                        parse_mode=ParseMode.MARKDOWN,
                    )

        return awrapper

    return wrapper


@merissacallback(pattern="anoncb")
async def anon_callback_handler1(upd: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle anonymous admin verification callback."""
    callback = upd.callback_query
    _, chat_id, message_id, perm = callback.data.split("/")
    chat_id = int(chat_id)
    message_id = int(message_id)

    try:
        mem = await upd.effective_chat.get_member(user_id=callback.from_user.id)
    except Exception as e:
        return await callback.answer(f"Error: {e}", show_alert=True)

    if mem.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        await callback.answer("You're not an admin.", show_alert=True)
        msg_id = anon_callback_messages.pop((chat_id, message_id), None)
        if msg_id is not None:
            await dispatcher.bot.delete_message(chat_id, msg_id)
        return await dispatcher.bot.send_message(
            chat_id, "You lack the permissions required for this command"
        )

    elif (
        getattr(mem, perm, False)
        or mem.status == ChatMemberStatus.OWNER
        or mem.user.id in DEV_USERS
    ):
        cb = anon_callbacks.pop((chat_id, message_id), None)
        if cb:
            msg_id = anon_callback_messages.pop((chat_id, message_id), None)
            if msg_id is not None:
                await dispatcher.bot.delete_message(chat_id, msg_id)
            return await cb[1](cb[0][0], cb[0][1])

    else:
        return await callback.answer("This isn't for you.", show_alert=True)


async def resolve_user(user: User, message_id: int, chat: Chat):
    """Resolve anonymous user to real user when sender_chat is anonymous."""
    if user.id == 1087968824:  # PTB's Anonymous admin system user
        try:
            uid = anon_users.pop((chat.id, message_id))
            user = (await chat.get_member(uid)).user
        except KeyError:
            return await dispatcher.bot.edit_message_text(
                chat_id=chat.id,
                message_id=message_id,
                text=f"You're now identified as: {user.first_name}",
            )
        except Exception as e:
            return await dispatcher.bot.edit_message_text(
                chat_id=chat.id, message_id=message_id, text=f"Error: {e}"
            )

    return user
