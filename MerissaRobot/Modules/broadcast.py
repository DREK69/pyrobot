import asyncio

from pyrogram import filters
from pyrogram.errors import FloodWait

from MerissaRobot import OWNER_ID, pbot
from MerissaRobot.Database.sql.users_sql import get_all_chats, get_all_users


@pbot.on_message(
    filters.command(["broadcastall", "broadcastgroups", "broadcastusers"])
    & filters.user(OWNER_ID)
)
async def broadcast(_, message):
    if message.reply_to_message:
        x = message.reply_to_message.id
        y = message.chat.id
    else:
        if len(message.command) < 2:
            return await message.reply_text(
                "**Usage**:\n/broadcast [MESSAGE] or [Reply to a Message]"
            )
    to_send = message.text.split(None, 1)
    if len(to_send) >= 2:
        to_group = False
        to_user = False
        if to_send[0] == "/broadcastgroups":
            to_group = True
        if to_send[0] == "/broadcastusers":
            to_user = True
        else:
            to_group = to_user = True
        if message.reply_to_message:
            x = message.reply_to_message.id
            y = message.chat.id
        else:
            if len(message.command) < 2:
                return await message.reply_text(
                    "**Usage**:\n/broadcast [MESSAGE] or [Reply to a Message]"
                )
        query = to_send[1]
        sent_group = 0
        sent_user = 0
        chats = get_all_chats() or []
        users = get_all_users()
        broadcast = await message.reply_text(
            "**Usage**:\n/broadcast [MESSAGE] or [Reply to a Message]"
        )
        if to_group:
            for chat in chats:
                try:
                    chat_id = int(chat.chat_id)
                    await pbot.forward_messages(
                        chat_id, y, x
                    ) if message.reply_to_message else await pbot.send_message(
                        chat_id, text=query
                    )
                    sent_group += 1
                except FloodWait as e:
                    flood_time = int(e.x)
                    if flood_time > 200:
                        continue
                    await asyncio.sleep(flood_time)
                except Exception:
                    continue
        if to_user:
            for user in users:
                try:
                    chat_id = int(user.user_id)
                    await pbot.forward_messages(
                        chat_id, y, x
                    ) if message.reply_to_message else await pbot.send_message(
                        chat_id, text=query
                    )
                except FloodWait as e:
                    flood_time = int(e.x)
                    if flood_time > 200:
                        continue
                    await asyncio.sleep(flood_time)
                except Exception:
                    continue
        try:
            await broadcast.edit_text(
                f"**Broadcast complete.\nGroups Count: {sent_group}\nUsers Count: {sent_user}**"
            )
        except:
            pass
