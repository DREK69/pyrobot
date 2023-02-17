import os
import wget
from pyrogram import filters

from MerissaRobot import pbot as bot


@bot.on_message(filters.command("asupan"))
async def animememes(_, message):
    x = await message.reply_text("Please Wait Video Uploading...")
    res = wget.download("https://api.princexd.tech/asupan/tiktok", "asupan.mp4")
    await message.reply_video("asupan.mp4")
    await x.delete()
    os.remove("asupan.mp4")
