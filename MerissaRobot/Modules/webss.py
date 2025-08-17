from base64 import b64decode
from inspect import getfullargspec
from io import BytesIO

from pyrogram import filters
from pyrogram.types import Message

from MerissaRobot import pbot as app
from MerissaRobot.helpers import postreq


async def take_screenshot(url: str, full: bool = False):
    """Fetch screenshot from external API"""
    url = "https://" + url if not url.startswith("http") else url
    payload = {
        "url": url,
        "width": 1920,
        "height": 1080,
        "scale": 1,
        "format": "jpeg",
    }
    if full:
        payload["full"] = True

    try:
        data = await postreq("https://webscreenshot.vercel.app/api", data=payload)
    except Exception as e:
        return None, f"API request failed: {e}"

    if not isinstance(data, dict) or "image" not in data:
        return None, "Invalid response from screenshot API."

    try:
        b = data["image"].replace("data:image/jpeg;base64,", "")
        file = BytesIO(b64decode(b))
        file.name = "screenshot.jpg"
        return file, None
    except Exception as e:
        return None, f"Failed to decode image: {e}"


async def eor(msg: Message, **kwargs):
    """Smart edit-or-reply"""
    func = msg.edit_text if msg.from_user and msg.from_user.is_self else msg.reply
    spec = getfullargspec(func).args
    return await func(**{k: v for k, v in kwargs.items() if k in spec})


@app.on_message(filters.command(["webss", "ss", "webshot"]))
async def take_ss(_, message: Message):
    """Capture website screenshot"""
    if len(message.command) < 2:
        return await eor(message, text="❌ Please provide a URL.\n\nExample: `/webss github.com`")

    url = message.command[1]
    full = False
    if len(message.command) > 2:
        full = message.command[2].lower().strip() in ["yes", "y", "1", "true", "full"]

    status = await eor(message, text="📸 Capturing screenshot...")

    photo, error = await take_screenshot(url, full)
    if error:
        return await status.edit(f"❌ {error}")

    if not photo:
        return await status.edit("⚠️ Failed to capture screenshot.")

    try:
        if full:
            await message.reply_document(photo, caption=f"🌐 Screenshot of: `{url}`\n(Full Page)")
        else:
            await message.reply_photo(photo, caption=f"🌐 Screenshot of: `{url}`")
        await status.delete()
    except Exception as e:
        await status.edit(f"❌ Upload failed: `{e}`")
