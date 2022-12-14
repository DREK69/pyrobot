from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from MerissaRobot import pbot


@pbot.on_message(filters.command("mod"))
async def movie(_, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "Give me some App/Game Name\n\nEx. `/mod Subway Surfer`"
        )
    name = (
        message.text.split(None, 1)[1]
        if len(message.command) < 3
        else message.text.split(None, 1)[1].replace(" ", "%20")
    )
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "📥 Download Mod APK",
                    url=f"https://happymod.com/search.html?q={name}",
                ),
            ],
        ]
    )
    await message.reply_text(
        f"Hi Dear, Your Download link is Ready\n\nClick Below Button To Download Mod APK\n\nPowered by @MerissaRobot",
        reply_markup=button,
    )
