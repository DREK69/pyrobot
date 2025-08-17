import asyncio
from pyrogram import filters
from pyrogram.errors import FloodWait
from MerissaRobot import pbot

SPAM_CHATS = set()  # better to use set instead of list


@pbot.on_message(filters.command(["tagall", "all"]) & filters.group)
async def tag_all_users(client, message):
    chat_id = message.chat.id
    replied = message.reply_to_message
    text = None

    if replied:
        text = replied.text or replied.caption or ""
    elif len(message.command) > 1:
        text = message.text.split(None, 1)[1]
    else:
        return await message.reply_text(
            "⚠️ Reply to a message or give me some text to mention others!"
        )

    if chat_id in SPAM_CHATS:
        return await message.reply_text("⚠️ Tag process already running here. Use /cancel to stop.")

    SPAM_CHATS.add(chat_id)
    usernum = 0
    usertxt = ""

    try:
        async for m in client.get_chat_members(chat_id):
            if chat_id not in SPAM_CHATS:
                break

            # Skip bots
            if m.user.is_bot:
                continue

            usernum += 1
            usertxt += f"⊚ [{m.user.first_name}](tg://user?id={m.user.id})\n"

            # Send message after 5 users (to avoid long msg issue)
            if usernum == 5:
                try:
                    await client.send_message(chat_id, f"{text}\n{usertxt}")
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    await client.send_message(chat_id, f"{text}\n{usertxt}")

                await asyncio.sleep(2)  # small delay for safety
                usernum = 0
                usertxt = ""

    finally:
        if chat_id in SPAM_CHATS:
            SPAM_CHATS.remove(chat_id)


@pbot.on_message(filters.command("cancel") & ~filters.private)
async def cancelcmd(_, message):
    chat_id = message.chat.id
    if chat_id in SPAM_CHATS:
        SPAM_CHATS.remove(chat_id)
        await message.reply_text("✅ Tagging process stopped!")
    else:
        await message.reply_text("⚠️ No tagging process is running here.")
