import os
import re
import aiofiles
from pyrogram import filters
from pyrogram.types import Message

from MerissaRobot import pbot as app
from MerissaRobot.Handler.pyro.errors import capture_err
from MerissaRobot.Handler.pyro.pastebin import paste

# Regex pattern for text-like mime types
pattern = re.compile(r"^text/|json$|yaml$|xml$|toml$|x-sh$|x-shellscript$")


@app.on_message(filters.command("paste"))
@capture_err
async def paste_func(_, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("⚠️ Reply to a message or file with `/paste`")

    m = await message.reply_text("⏳ Pasting...")

    content = None

    # Case 1: Reply contains plain text
    if message.reply_to_message.text:
        content = message.reply_to_message.text

    # Case 2: Reply contains document (like .txt, .json, .yaml, etc.)
    elif message.reply_to_message.document:
        document = message.reply_to_message.document

        if document.file_size > 1048576:  # 1MB
            return await m.edit("❌ File too large! Only files < 1MB can be pasted.")

        if not document.mime_type or not pattern.search(document.mime_type):
            return await m.edit("❌ Only text-based files can be pasted.")

        doc_path = await message.reply_to_message.download()

        async with aiofiles.open(doc_path, mode="r") as f:
            content = await f.read()

        os.remove(doc_path)

    # No valid content found
    if not content:
        return await m.edit("❌ Unsupported message type for paste.")

    # Upload to paste service
    try:
        link = await paste(content)
    except Exception as e:
        return await m.edit(f"❌ Failed to paste: `{e}`")

    return await m.edit(f"✅ Pasted successfully:\n{link}")
