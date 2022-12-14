import os

from pyrogram import filters

from MerissaRobot import pbot as bot


@bot.on_message(filters.command("rename"))
def rename(_, message):

    try:
        filename = message.text.replace(message.text.split(" ")[0], "")

    except AttributeError:
        update.message.reply_text("pls report @MerissaxSupport")

    reply = message.reply_to_message
    if reply:
        x = message.reply_text("📥 Downloading.....")
        path = reply.download(file_name=filename)
        x.edit("📤 Uploading.....")
        message.reply_document(path)
        os.remove(path)
