from telegram import Chat, User

async def user_can_promote(chat: Chat, user: User, bot_id: int) -> bool:
    member = await chat.get_member(user.id)
    bot_member = await chat.get_member(bot_id)
    return bool(getattr(member, "can_promote_members", False)) and bool(getattr(bot_member, "can_promote_members", False))

async def user_can_ban(chat: Chat, user: User, bot_id: int) -> bool:
    member = await chat.get_member(user.id)
    bot_member = await chat.get_member(bot_id)
    return bool(getattr(member, "can_restrict_members", False)) and bool(getattr(bot_member, "can_restrict_members", False))

async def user_can_pin(chat: Chat, user: User, bot_id: int) -> bool:
    member = await chat.get_member(user.id)
    bot_member = await chat.get_member(bot_id)
    return bool(getattr(member, "can_pin_messages", False)) and bool(getattr(bot_member, "can_pin_messages", False))

async def user_can_changeinfo(chat: Chat, user: User, bot_id: int) -> bool:
    member = await chat.get_member(user.id)
    bot_member = await chat.get_member(bot_id)
    return bool(getattr(member, "can_change_info", False)) and bool(getattr(bot_member, "can_change_info", False))
