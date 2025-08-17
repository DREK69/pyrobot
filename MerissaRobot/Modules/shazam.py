import os
from pyrogram import filters, types
from shazamio import Shazam

from MerissaRobot import pbot
from MerissaRobot.Handler.pyro.ytmusic import ytmsearch
from MerissaRobot.helpers import subscribe

shazam = Shazam()


async def recognize(path: str):
    return await shazam.recognize_song(path)


@pbot.on_message(filters.command("shazam"))
@subscribe
async def voice_handler(client, message):
    if not message.reply_to_message:
        return await message.reply_text("⚠️ Please reply to an **audio, video, or voice message**.")

    media = (
        message.reply_to_message.audio
        or message.reply_to_message.video
        or message.reply_to_message.voice
    )
    if not media:
        return await message.reply_text("⚠️ Please reply with a valid **audio, video, or voice file**.")

    status = await message.reply_text("⬇️ Downloading media...")

    try:
        file = await message.reply_to_message.download()
        await status.edit_text("🔍 Recognizing the audio...")

        result = await recognize(file)
        track = result.get("track", None)

        # Clean up file
        if os.path.exists(file):
            os.remove(file)

        if not track:
            return await status.edit_text("❌ Could not recognize the audio.")

        await status.edit_text("✅ Found details for your media.")

        title = track.get("title", "Unknown")
        artist = track.get("subtitle", "Unknown")
        cover = track["images"].get("coverarthq") if track.get("images") else None
        share_link = track.get("share", {}).get("html", "")
        listen_url = track.get("url", "")

        # Search song on YouTube Music
        query = f"{title} - {artist}"
        search = await ytmsearch(query) if callable(ytmsearch) else ytmsearch(query)
        videoid = search["results"][0]["videoId"] if search and search.get("results") else None

        out = f"**🎵 Title:** `{title}`\n**👤 Artist:** `{artist}`\n"

        buttons = [
            [
                types.InlineKeyboardButton("🔗 Share", url=share_link),
                types.InlineKeyboardButton("🎧 Listen", url=listen_url),
            ]
        ]

        if videoid:
            buttons.append(
                [types.InlineKeyboardButton("📥 Download Song", callback_data=f"audio {videoid}")]
            )

        if cover:
            await message.reply_photo(
                cover,
                caption=out,
                reply_markup=types.InlineKeyboardMarkup(buttons),
            )
        else:
            await message.reply_text(out, reply_markup=types.InlineKeyboardMarkup(buttons))

        await status.delete()

    except Exception as e:
        if os.path.exists(file):
            os.remove(file)
        return await status.edit_text(f"⚠️ Error: `{str(e)}`")
