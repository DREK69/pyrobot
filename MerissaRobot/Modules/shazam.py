import os

from pyrogram import filters, types
from shazamio import Shazam

from MerissaRobot import pbot

shazam = Shazam()


async def recognize(path):
    return await shazam.recognize_song(path)


@pbot.on_message(filters.audio | filters.video | filters.voice)
async def voice_handler(_, message):
    file_size = message.audio or message.video or message.voice
    if 30641629 < file_size.file_size:
        await message.reply_text("**⚠️ Max file size has been reached.**")
        return
    file = await message.download("merissa.mp3")
    r = (await recognize(file)).get("track", None)
    os.remove(file)
    if r is None:
        await message.reply_text("**⚠️ Cannot recognize the audio**")
        return
    out = f'**Title**: `{r["title"]}`\n'
    out += f'**Artist**: `{r["subtitle"]}`\n'
    buttons = [
        [
            types.InlineKeyboardButton("🔗 Share", url=f'{r["share"]["html"]}'),
            types.InlineKeyboardButton("🎵 Listen", url=f'{r["url"]}'),
        ],
    ]
    await message.reply_photo(
        r["images"]["coverarthq"],
        caption=out,
        reply_markup=types.InlineKeyboardMarkup(buttons),
    )
