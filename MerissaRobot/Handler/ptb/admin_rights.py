from telegram import Chat, User
from telegram.ext import ContextTypes

async def user_can_promote(chat: Chat, user: User, bot_id: int) -> bool:
    member = await chat.get_member(user.id)
    return member.can_promote_members

async def user_can_ban(chat: Chat, user: User, bot_id: int) -> bool:
    member = await chat.get_member(user.id)
    return member.can_restrict_members

async def user_can_pin(chat: Chat, user: User, bot_id: int) -> bool:
    member = await chat.get_member(user.id)
    return member.can_pin_messages

async def user_can_changeinfo(chat: Chat, user: User, bot_id: int) -> bool:
    member = await chat.get_member(user.id)
    return member.can_change_info
