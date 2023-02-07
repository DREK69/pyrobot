from pyrogram import filters
from requests import get

from MerissaRobot import pbot


@pbot.on_message(filters.command("insta"))
async def instadown(_, message):
    if len(message.command) < 2:
        return await message.reply_text("Give me some link\n\nEx. /insta link")
    name = (
        message.text.split(None, 1)[1]
        if len(message.command) < 3
        else message.text.split(None, 1)[1].replace(" ", "%20")
    )
    x = get(f"https://api.princexd.tech/igdown?link={name}").json()["media"]
    await message.reply_video(
        x,
        caption="Powered by @MerissaRobot",
    )
