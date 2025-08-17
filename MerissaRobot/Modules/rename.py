import os
from pyrogram import filters
from MerissaRobot import pbot as bot


@bot.on_message(filters.command("rename"))
async def rename(_, message):
    if not message.reply_to_message or not message.reply_to_message.document:
        return await message.reply_text("❌ Reply to a file to rename it.")

    if len(message.command) < 2:
        return await message.reply_text("⚠️ Usage: `/rename newfilename.ext`", quote=True)

    reply = message.reply_to_message
    filename = " ".join(message.command[1:])  # extract new filename

    if reply.document.file_size > 10 * 1024 * 1024:  # 10MB
        return await message.reply_text("⚠️ You can only rename files smaller than 10MB.")

    status = await message.reply_text("📥 Downloading...")

    try:
        # Download with new name
        path = await reply.download(file_name=filename)

        await status.edit("📤 Uploading...")
        await message.reply_document(path, caption=f"✅ Renamed to `{filename}`")

    except Exception as e:
        await status.edit(f"❌ Error: {e}")

    finally:
        if os.path.exists(path):
            os.remove(path)
        await status
