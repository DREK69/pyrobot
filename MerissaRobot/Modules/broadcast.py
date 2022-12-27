#
# Copyright (C) 2021-2022 by TeamYukki@Github, < https://github.com/TeamYukki >.
#
# This file is part of < https://github.com/TeamYukki/YukkiAFKBot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/TeamYukki/YukkiAFKBot/blob/master/LICENSE >
#
# All rights reserved.
#


import asyncio

from pyrogram import filters
from pyrogram.errors import FloodWait

from MerissaRobot import OWNER_ID as SUDOERS
from MerissaRobot import pbot as app
from MerissaRobot.Database.mongo.chats_mongo import get_served_chats


@app.on_message(filters.command("broadcast") & filters.user(SUDOERS))
async def broadcast(_, message):
    if message.reply_to_message:
        x = message.reply_to_message.message_id
        y = message.chat.id
    else:
        if len(message.command) < 2:
            return await message.reply_text(
                "**Usage**:\n/broadcast [MESSAGE] or [Reply to a Message]"
            )
        query = message.text.split(None, 1)[1]
    sent = 0
    chats = []
    schats = await get_served_chats()
    for chat in schats:
        chats.append(int(chat["chat_id"]))
    for i in chats:
        try:
            await app.forward_messages(
                i, y, x
            ) if message.reply_to_message else await app.send_message(i, text=query)
            sent += 1
        except FloodWait as e:
            flood_time = int(e.x)
            if flood_time > 200:
                continue
            await asyncio.sleep(flood_time)
        except Exception:
            continue
    try:
        await message.reply_text(f"**Broadcasted Message In {sent} Chats.**")
    except:
        pass
