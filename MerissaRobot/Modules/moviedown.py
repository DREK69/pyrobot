from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from MerissaRobot import pbot


@pbot.on_message(filters.command("movie"))
async def movie(_, message):
    if len(message.command) < 2:
        return await message.reply_text("Give me some Movie Name\n\nEx. /movie Kgf 2")
    name = (
        message.text.split(None, 1)[1]
        if len(message.command) < 3
        else message.text.split(None, 1)[1].replace(" ", "%20")
    )
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Link", url=f"https://vegamovies.page/?s={name}"
                ),
                InlineKeyboardButton(
                    "Link", url=f"https://dotmovies.xyz/?s={name}"
                ),
            ],
        ]
    )
    await message.reply_text(
        f"Hi Dear, Your Movie Download link is Ready\n\nTry Both Links\n\nPowered by @MerissaRobot",
        reply_markup=button,
    )
