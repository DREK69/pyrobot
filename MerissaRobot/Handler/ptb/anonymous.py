import functools
from enum import Enum
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, Message
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
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
    CREATOR = "creator"
    ADMIN = "administrator"


anon_callbacks = {}
anon_callback_messages = {}
anon_users = {}


def user_admin(permission: AdminPerms):
    def wrapper(func):
        @functools.wraps(func)
        async def awrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            nonlocal permission
            if update.effective_chat.type == "private":
                return await func(update, context, *args, **kwargs)

            message: Message = update.effective_message
            is_anon = message.sender_chat

            if is_anon:
                callback_id = f"anoncb/{message.chat.id}/{message.message_id}/{permission.value}"
                anon_callbacks[(message.chat.id, message.message_id)] = ((update, context), func)

                sent_msg = await message.reply_text(
                    "Seems like you're anonymous, click the button below to prove your identity",
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="Prove identity", callback_data=callback_id)]]
                    ),
                )
                anon_callback_messages[(message.chat.id, message.message_id)] = sent_msg.message_id

            else:
                user_id = message.from_user.id
                chat_id = message.chat.id
                mem = await context.bot.get_chat_member(chat_id=chat_id, user_id=user_id)

                if (
                    getattr(mem, permission.value, False) is True
                    or mem.status == "creator"
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
    callback = upd.callback_query
    perm = callback.data.split("/")[3]
    chat_id = int(callback.data.split("/")[1])
    message_id = int(callback.data.split("/")[2])

    try:
        mem = await upd.effective_chat.get_member(user_id=callback.from_user.id)
    except BaseException as e:
        await callback.answer(f"Error: {e}", show_alert=True)
        return

    if mem.status not in [ChatStatus.ADMIN.value, ChatStatus.CREATOR.value]:
        await callback.answer("You're aren't admin.")
        msg_id = anon_callback_messages.pop((chat_id, message_id), None)
        if msg_id is not None:
            await dispatcher.bot.delete_message(chat_id, msg_id)
        await dispatcher.bot.send_message(
            chat_id, "You lack the permissions required for this command"
        )

    elif (
        getattr(mem, perm, False) is True
        or mem.status == "creator"
        or mem.user.id in DEV_USERS
    ):
        cb = anon_callbacks.pop((chat_id, message_id), None)
        if cb:
            msg_id = anon_callback_messages.pop((chat_id, message_id), None)
            if msg_id is not None:
                await dispatcher.bot.delete_message(chat_id, msg_id)
            return await cb[1](cb[0][0], cb[0][1])
    else:
        await callback.answer("This isn't for ya")


async def resolve_user(user, message_id, chat):
    if user.id == 1087968824:
        try:
            uid = anon_users.pop((chat.id, message_id))
            user = (await chat.get_member(uid)).user
        except KeyError:
            return await dispatcher.bot.edit_message_text(
                chat_id=chat.id,
                message_id=message_id,
                text="You're now identified as: {}".format(user.first_name),
            )
        except BaseException as e:
            return await dispatcher.bot.edit_message_text(
                chat_id=chat.id, message_id=message_id, text=f"Error: {e}"
            )

    return user        or mem.user.id in DEV_USERS
    ):
        cb = anon_callbacks.pop((chat_id, message_id), None)
        if cb:
            message_id = anon_callback_messages.pop((chat_id, message_id), None)
            if message_id is not None:
                dispatcher.bot.delete_message(chat_id, message_id)
            return cb[1](cb[0][0], cb[0][1])
    else:
        callback.answer("This isn't for ya")


def resolve_user(user, message_id, chat):
    if user.id == 1087968824:
        try:
            uid = anon_users.pop((chat.id, message_id))
            user = chat.get_member(uid).user
        except KeyError:
            return dispatcher.bot.edit_message_text(
                chat.id,
                message_id,
                "You're now identified as: {}".format(user.first_name),
            )
        except BaseException as e:
            return dispatcher.bot.edit_message_text(chat.id, message_id, f"Error: {e}")

    else:
        user = user
    return user
