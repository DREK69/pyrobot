from pyrogram import filters
from requests import get

from MerissaRobot import pbot


@pbot.on_message(filters.command("genmail"))
async def gen_mail(_, message):
    x = get(f"https://api.princexd.tech/emailgen").json()["email"]
    await message.reply_text(
        f"Email - {x}\n\nPowered by @MerissaRobot",
    )


@pbot.on_message(filters.command("mails"))
async def movie(_, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "First of all Genrate Email /genmail and Give me some emails to get mails\n\nEx. /mails abcdef@coooooool.com"
        )
    email = (
        message.text.split(None, 1)[1]
        if len(message.command) < 3
        else message.text.split(None, 1)[1].replace(" ", "%20")
    )
    x = get(f"https://api.princexd.tech/receivedmails?email={email}").json()[0][
        "body_text"
    ]
    cu = x["from"]
    From = cu.replace("<","").replace(">", "")
    to = x["to"]
    subject = x["subject"]
    text = x["body_text"]
    await message.reply_text(
        text=f"From = {fr}\nTo = {to}\n\nSubject = {subject}\nBody = {text}\n\nPowered By @MerissaRobot",
    )
