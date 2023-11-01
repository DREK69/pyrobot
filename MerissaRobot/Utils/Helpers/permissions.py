from functools import wraps

from pyrogram.errors.exceptions.forbidden_403 import ChatWriteForbidden
from pyrogram.types import Message

from MerissaRobot import DEMONS, DEV_USERS, DRAGONS, TIGERS, WOLVES
from MerissaRobot import pbot as app

SUDO = DRAGONS, DEV_USERS, WOLVES, DEMONS, TIGERS


async def member_permissions(chat_id: int, user_id: int):
    perms = []
    member = await app.get_chat_member(chat_id, user_id)
    if member.privileges.can_post_messages:
        perms.append("can_post_messages")
    if member.privileges.can_edit_messages:
        perms.append("can_edit_messages")
    if member.privileges.can_delete_messages:
        perms.append("can_delete_messages")
    if member.privileges.can_restrict_members:
        perms.append("can_restrict_members")
    if member.privileges.can_promote_members:
        perms.append("can_promote_members")
    if member.privileges.can_change_info:
        perms.append("can_change_info")
    if member.privileges.can_invite_users:
        perms.append("can_invite_users")
    if member.privileges.can_pin_messages:
        perms.append("can_pin_messages")
    if member.privileges.can_manage_voice_chats:
        perms.append("can_manage_voice_chats")
    return perms


async def authorised(func, subFunc2, client, message, *args, **kwargs):
    chatID = message.chat.id
    try:
        await func(client, message, *args, **kwargs)
    except ChatWriteForbidden:
        await app.leave_chat(chatID)
    except Exception as e:
        try:
            await message.reply_text(str(e))
        except ChatWriteForbidden:
            await app.leave_chat(chatID)
    return subFunc2


async def unauthorised(message: Message, permission, subFunc2):
    chatID = message.chat.id
    text = (
        "You don't have the required permission to perform this action."
        + f"\n**Permission:** __{permission}__"
    )
    try:
        await message.reply_text(text)
    except ChatWriteForbidden:
        await app.leave_chat(chatID)
    return subFunc2


def adminsOnly(permission):
    def subFunc(func):
        @wraps(func)
        async def subFunc2(client, message: Message, *args, **kwargs):
            chatID = message.chat.id
            if not message.from_user:
                # For anonymous admins
                if message.sender_chat:
                    return await authorised(
                        func, subFunc2, client, message, *args, **kwargs
                    )
                return await unauthorised(message, permission, subFunc2)
            # For admins and sudo users
            userID = message.from_user.id
            permissions = await member_permissions(chatID, userID)
            if userID not in SUDO and permission not in permissions:
                return await unauthorised(message, permission, subFunc2)
            return await authorised(func, subFunc2, client, message, *args, **kwargs)

        return subFunc2

    return subFunc


async def edit_or_reply(message, text, parse_mode="md"):
    if message.from_user.id:
        if message.reply_to_message:
            kk = message.reply_to_message.message_id
            return await message.reply_text(
                text, reply_to_message_id=kk, parse_mode=parse_mode
            )
        return await message.reply_text(text, parse_mode=parse_mode)
    return await message.edit(text, parse_mode=parse_mode)
