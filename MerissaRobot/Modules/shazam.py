import os

from pyrogram import filters, types
from shazamio import Shazam

from MerissaRobot import pbot
from MerissaRobot.Handler.pyro.ytmusic import ytmsearch
from MerissaRobot.helpers import subscribe

shazam = Shazam()


async def recognize(path):
    return await shazam.recognize_song(path)


@pbot.on_message(filters.command("shazam"))
@subscribe
async def voice_handler(client, message):
    message.from_user.id
    media = (
        message.reply_to_message.audio
        or message.reply_to_message.video
        or message.reply_to_message.voice
    )
    if not media:
        return await message.reply_text("Please Reply to Audio, Video, Voice")
    ok = await message.reply_text("Downloading Media...")
    file = await message.reply_to_message.download()
    await ok.edit_text("Recognise your Sended media")
    r = (await recognize(file)).get("track", None)
    os.remove(file)
    if r is None:
        await ok.edit_text("**⚠️ Cannot recognize the audio**")
        return
    await ok.edit_text("Details Founded of Your Media")
    out = f'**Title**: `{r["title"]}`\n'
    out += f'**Artist**: `{r["subtitle"]}`\n'
    query = f"{r['title']} - {r['subtitle']}"
    search = ytmsearch(query)
    videoid = search["results"][0]["videoId"]
    buttons = [
        [
            types.InlineKeyboardButton("🔗 Share", url=f'{r["share"]["html"]}'),
            types.InlineKeyboardButton("🎵 Listen", url=f'{r["url"]}'),
        ],
        [
            types.InlineKeyboardButton(
                "📥 Download Song", callback_data=f"audio {videoid}"
            ),
        ],
    ]
    await ok.delete("Uploading Song Details...")
    await message.reply_photo(
        r["images"]["coverarthq"],
        caption=out,
        reply_markup=types.InlineKeyboardMarkup(buttons),
    )
    await ok.delete()
