import re
import asyncio
from typing import List, Optional, Tuple
from telegram import Message, MessageEntity
from telegram.error import BadRequest
from MerissaRobot import LOGGER
from MerissaRobot.Modules.users import get_user_id


def id_from_reply(message: Message) -> Tuple[Optional[int], Optional[str]]:
    """Extract user ID and text from reply message (sync)."""
    prev_message = message.reply_to_message
    if not prev_message or not prev_message.from_user:
        return None, None
    user_id = prev_message.from_user.id
    res = message.text.split(None, 1)
    return user_id, (res[1] if len(res) > 1 else "")


async def extract_user_and_text(
    message: Message, args: List[str]
) -> Tuple[Optional[int], Optional[str]]:
    """Extract user ID and optional text from a command message."""
    prev_message = message.reply_to_message
    split_text = message.text.split(None, 1)
    text = ""

    # Case 1: reply
    if not args and prev_message:
        return id_from_reply(message)

    # Case 2: text mention (explicit user object in entity)
    entities = message.parse_entities([MessageEntity.TEXT_MENTION])
    if entities:
        for ent, val in entities.items():
            if ent.user:
                user_id = ent.user.id
                text = message.text[ent.offset + ent.length :]
                return user_id, text.strip()

    # Case 3: @username
    if args and args[0].startswith("@"):
        username = args[0]
        user_id = (
            await get_user_id(username)
            if asyncio.iscoroutinefunction(get_user_id)
            else get_user_id(username)
        )
        if not user_id:
            await message.reply_text(
                "I don't know this user. Reply to a message from them or forward one of their messages."
            )
            return None, None
        if len(args) > 1:
            text = " ".join(args[1:])
        return user_id, text

    # Case 4: numeric ID or t.me link
    if args:
        arg = args[0]
        if arg.isdigit():
            user_id = int(arg)
        else:
            m = re.match(r"https://t\.me/(\w+)", arg)
            if m:
                username = m.group(1)
                user_id = (
                    await get_user_id(f"@{username}")
                    if asyncio.iscoroutinefunction(get_user_id)
                    else get_user_id(f"@{username}")
                )
            else:
                user_id = None
        if not user_id:
            await message.reply_text(
                "I couldn't resolve this user. Try replying to them instead."
            )
            return None, None
        if len(args) > 1:
            text = " ".join(args[1:])
        return user_id, text

    return None, None


async def extract_user(message: Message, args: List[str]) -> Optional[int]:
    """Wrapper to only return user_id."""
    user_id, _ = await extract_user_and_text(message, args)
    return user_id


def extract_text(message: Message) -> str:
    """Extract plain text or caption from message."""
    return (
        message.text
        or message.caption
        or (message.sticker.emoji if message.sticker else "")
    )


async def extract_unt_fedban(
    message: Message, args: List[str]
) -> Tuple[Optional[int], Optional[str]]:
    """Special extractor for federation ban commands."""
    user_id, text = await extract_user_and_text(message, args)

    if not user_id:
        return None, None

    # Verify user (best effort, but don't hard fail on 'Chat not found')
    try:
        await message.get_bot().get_chat(user_id)
    except BadRequest as excp:
        if excp.message in ("User_id_invalid", "Chat not found"):
            await message.reply_text(
                "I haven't seen this user before. Forward one of their messages so I can identify them."
            )
            return None, None
        LOGGER.exception("Exception %s on user %s", excp.message, user_id)
        return None, None

    return user_id, text


async def extract_user_fban(message: Message, args: List[str]) -> Optional[int]:
    """Wrapper for federation ban use-case (only ID)."""
    user_id, _ = await extract_unt_fedban(message, args)
    return user_id
