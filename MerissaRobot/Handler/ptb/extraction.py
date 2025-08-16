import re
from typing import List, Optional, Tuple
from telegram import Message, MessageEntity
from telegram.error import BadRequest
from MerissaRobot import LOGGER
from MerissaRobot.Modules.users import get_user_id


def id_from_reply(message: Message) -> Tuple[Optional[int], Optional[str]]:
    """Extract user ID and text from reply message - this function stays sync"""
    prev_message = message.reply_to_message
    if not prev_message:
        return None, None
    user_id = prev_message.from_user.id
    res = message.text.split(None, 1)
    if len(res) < 2:
        return user_id, ""
    return user_id, res[1]


async def extract_user(message: Message, args: List[str]) -> Optional[int]:
    """Extract user ID from message arguments"""
    return (await extract_user_and_text(message, args))


async def extract_user_and_text(
    message: Message, args: List[str]
) -> Tuple[Optional[int], Optional[str]]:
    """Extract user ID and associated text from message"""
    prev_message = message.reply_to_message
    split_text = message.text.split(None, 1)

    if len(split_text) < 2:
        return id_from_reply(message)

    text_to_parse = split_text[1]
    text = ""

    # Handle text mentions
    entities = list(message.parse_entities([MessageEntity.TEXT_MENTION]))
    ent = entities if entities else None

    if entities and ent and ent.offset == len(message.text) - len(text_to_parse):
        user_id = ent.user.id
        text = message.text[ent.offset + ent.length :]

    # Handle username mentions
    elif len(args) >= 1 and args.startswith("@"):
        user = args
        # Make sure get_user_id is async if it makes database calls
        if hasattr(get_user_id, '__call__'):
            if asyncio.iscoroutinefunction(get_user_id):
                user_id = await get_user_id(user)
            else:
                user_id = get_user_id(user)
        else:
            user_id = get_user_id(user)
            
        if not user_id:
            await message.reply_text(
                "No idea who this user is. You'll be able to interact with them if "
                "you reply to that person's message instead, or forward one of that user's messages."
            )
            return None, None

    # Handle user ID or Telegram link
    elif len(args) >= 1 and (
        args[0].isdigit() or re.match(r"https://t\.me/(\w+)", args)
    ):
        if args.isdigit():
            user_id = int(args)
        else:
            username = re.search(r"https://t\.me/(\w+)", args).group(1)
            # Handle async get_user_id
            if hasattr(get_user_id, '__call__'):
                if asyncio.iscoroutinefunction(get_user_id):
                    user_id = await get_user_id(f"@{username}")
                else:
                    user_id = get_user_id(f"@{username}")
            else:
                user_id = get_user_id(f"@{username}")

        if not user_id:
            await message.reply_text(
                "No idea who this user is. You'll be able to interact with them if "
                "you reply to that person's message instead, or forward one of that user's messages."
            )
            return None, None

    # Handle reply messages
    elif prev_message:
        user_id, text = id_from_reply(message)

    else:
        return None, None

    # Validate user exists - Updated for PTB v22
    try:
        # Use context.bot instead of message.get_bot() if you have access to context
        # For now, keeping the existing pattern but ensuring it works with v22
        chat_info = await message.get_bot().get_chat(user_id)
        if chat_info.type not in ["private", "bot"]:
            raise BadRequest("Chat is not a private chat or a bot")
    except BadRequest as excp:
        if excp.message in ("User_id_invalid", "Chat not found"):
            await message.reply_text(
                "Sorry, I could not find the user you specified. Please make sure that you "
                "have spelled their username or user ID correctly and that they have interacted "
                "with me before."
            )
        else:
            LOGGER.exception("Exception %s on user %s", excp.message, user_id)
            await message.reply_text(
                "Sorry, an error occurred while processing your request. Please try again later."
            )
        return None, None

    return user_id, text


def extract_text(message: Message) -> str:
    """Extract text from message - stays sync as it's just text processing"""
    return (
        message.text
        or message.caption
        or (message.sticker.emoji if message.sticker else None)
    )


async def extract_unt_fedban(
    message: Message, args: List[str]
) -> Tuple[Optional[int], Optional[str]]:
    """Extract user and text for federation ban operations"""
    prev_message = message.reply_to_message
    split_text = message.text.split(None, 1)

    if len(split_text) < 2:
        return id_from_reply(message)

    text = ""
    entities = list(message.parse_entities([MessageEntity.TEXT_MENTION]))
    ent = entities[0] if entities else None

    # Handle text mentions
    if entities and ent and ent.offset == len(message.text) - len(split_text[1]):
        user_id = ent.user.id
        text = message.text[ent.offset + ent.length :]

    # Handle username mentions
    elif len(args) >= 1 and args.startswith("@"):
        # Handle async get_user_id
        if hasattr(get_user_id, '__call__'):
            if asyncio.iscoroutinefunction(get_user_id):
                user_id = await get_user_id(args)
            else:
                user_id = get_user_id(args)
        else:
            user_id = get_user_id(args)
            
        if not user_id:
            await message.reply_text(
                "I don't have that user in my db. "
                "You'll be able to interact with them if you reply to that person's message instead, or forward one of that user's messages."
            )
            return None, None
        res = message.text.split(None, 2)
        if len(res) >= 3:
            text = res[2]

    # Handle user ID
    elif len(args) >= 1 and args.isdigit():
        user_id = int(args)
        res = message.text.split(None, 2)
        if len(res) >= 3:
            text = res[2]

    # Handle reply messages
    elif prev_message:
        user_id, text = id_from_reply(message)

    else:
        return None, None

    # Validate user exists
    try:
        await message.get_bot().get_chat(user_id)
    except BadRequest as excp:
        if excp.message in ("User_id_invalid", "Chat not found") and not isinstance(
            user_id, int
        ):
            await message.reply_text(
                "I don't seem to have interacted with this user before "
                "please forward a message from them to give me control!"
            )
            return None, None
        if excp.message != "Chat not found":
            LOGGER.exception("Exception %s on user %s", excp.message, user_id)
            return None, None
        if not isinstance(user_id, int):
            return None, None

    return user_id, text


async def extract_user_fban(message: Message, args: List[str]) -> Optional[int]:
    """Extract user ID for federation ban operations"""
    return (await extract_unt_fedban(message, args))[0]
    
