import os

from pyrogram import filters

from MerissaRobot import pbot as bot


@bot.on_message(filters.command("rename"))
def rename(_, message):

    try:
        filename = message.text.replace(message.text.split(" ")[0], "")

    except AttributeError:
        update.message.reply_text("pls report @MerissaxSupport")
    
    document = message.reply_to_message.document
    if document:
        if document.file_size > 10485760:
            return await m.edit("You can only rename files smaller than 10MB.")
        x = message.reply_text("📥 Downloading.....")
        path = document.download(file_name=filename)
        x.edit("📤 Uploading.....")
        message.reply_document(path)
        os.remove(path)
