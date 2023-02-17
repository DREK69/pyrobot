import requests
from pyrogram import filters
from pyrogram.types import *

from MerissaRobot import pbot as bot


@bot.on_message(filters.command("asupan"))
async def animememes(_, message):
    x = await message.reply_text("Please Wait Video Uploading...")
    res = requests.get("https://api.princexd.tech/asupan/tiktok").json()["url"]
    await message.reply_video(res)
    await x.delete()
