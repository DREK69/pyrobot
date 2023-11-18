import asyncio

from pyrogram import filters

from MerissaRobot import pbot, user
from MerissaRobot.helpers import subscribe


@pbot.on_message(filters.command("sg"))
@subscribe
async def sangmata(client, message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif not message.reply_to_message and len(message.command) == 1:
        user_id = message.from_user.id
    elif not message.reply_to_message and len(message.command) != 1:
        anu = message.text.split(None, 1)[1]
        iya = await client.get_users(anu)
        user_id = iya.id
    else:
        return await message.reply("__Reply to message or give Username/UserId__")
    sgbot = await message.reply("**🔍 Searching**")
    await user.unblock_user("@sangmata_beta_bot")
    sang = await user.send_message("SangMata_beta_bot", f" {user_id}")
    await sang.delete()
    await asyncio.sleep(3)
    async for msg in user.search_messages("SangMata_beta_bot", limit=4):
        if "This result is incomplete" or "Link To Profile" in msg.text:
            await msg.delete()
        if "No records found" in msg.text:
            await sgbot.edit("No Data Found")
            await msg.delete()
        if "Name" in msg.text:
            await sgbot.edit(msg.text)
            await msg.delete()


@pbot.on_message(filters.command("animate"))
@subscribe
async def convert_image(client, message):
    if not message.reply_to_message:
        return await message.reply_text("**Please Reply to photo**")
    if message.reply_to_message:
        await message.reply_text("`Processing...`")
    reply_message = message.reply_to_message
    photo = reply_message.photo.file_id
    bot = "qq_neural_anime_bot"
    await user.send_photo(bot, photo=photo)
    await asyncio.sleep(18)
    async for result in user.search_messages(bot, limit=3):
        if result.photo:
            await message.edit("Uploading...")
            converted_image_file = await user.download_media(result)
            await client.send_photo(
                message.chat.id,
                converted_image_file,
                caption="Powered By @MerissaRobot",
            )
            await message.delete()
        else:
            await message.edit("`Error message ...`")
