from pyrogram import filters
from requests import get

from MerissaRobot import pbot


@pbot.on_message(filters.command("ask"))
async def ask(_, message):
    m = await message.reply_text("Wait a moment looking for your answer..")
    if len(message.command) < 2:
        return await message.reply_text(
            "Give me some questions to ask ChatGPT. Example- /ask question"
        )
    query = (
        message.text.split(None, 1)[1]
        if len(message.command) < 3
        else message.text.split(None, 1)[1].replace(" ", "%20")
    )
    x = get(f"https://api.princexd.tech/ask?text={query}").json()["answer"]
    await m.edit(f"{x}\n\nPowered by @MerissaRobot", disable_web_page_preview=True)
