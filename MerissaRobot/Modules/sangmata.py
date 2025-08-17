import asyncio
from pyrogram import filters
from pyrogram.types import Message

from MerissaRobot import pbot, user
from MerissaRobot.helpers import subscribe


@pbot.on_message(filters.command("sg"))
@subscribe
async def sangmata(client, message: Message):
    """Fetch name history using SangMata bot"""
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif len(message.command) == 1:
        user_id = message.from_user.id
    else:
        try:
            arg = message.text.split(None, 1)[1]
            user_obj = await client.get_users(arg)
            user_id = user_obj.id
        except Exception:
            return await message.reply("__Invalid username or user ID given.__")

    sgbot = await message.reply("🔍 **Searching...**")

    # Make sure the bot is unblocked
    try:
        await user.unblock_user("sangmata_beta_bot")
    except Exception:
        pass

    # Send request to SangMata bot
    try:
        req = await user.send_message("sangmata_beta_bot", str(user_id))
        await asyncio.sleep(3)
    except Exception as e:
        return await sgbot.edit(f"❌ Failed to contact SangMata bot.\n`{e}`")

    found = False
    async for msg in user.search_messages("sangmata_beta_bot", limit=6):
        if not msg.text:
            continue

        if "No records found" in msg.text:
            await sgbot.edit("⚠️ No data found for this user.")
            await msg.delete()
            found = True
            break

        if "Name" in msg.text:  # valid SangMata result
            await sgbot.edit(f"📑 **Name History Found:**\n\n{msg.text}")
            await msg.delete()
            found = True
            break

        if "This result is incomplete" in msg.text or "Link To Profile" in msg.text:
            await msg.delete()

    if not found:
        await sgbot.edit("❌ Could not fetch data. Try again later.")
    
    # cleanup request
    try:
        await req.delete()
    except:
        pass
