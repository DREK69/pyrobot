from pyrogram import Client, filters
from pyrogram.types import InputMediaPhoto, Message

from MerissaRobot import pbot
from MerissaRobot.helpers import getreq, subscribe


@pbot.on_message(filters.command("google"))
@subscribe
async def google_search(_, message: Message):
    if len(message.command) < 2:
        return await message.reply_text(
            "Give me some query to search on google\n\nex: /google who is merissarobot?"
        )

    webevent = await message.reply_text("🔎 Searching...")
    query = message.text.split(None, 1)[1]

    gresults = await getreq(
        f"https://api.princexd.tech/google?query={query}&limit=5"
    )

    msg = ""
    for i in gresults.get("results", []):
        title = i.get("title")
        link = i.get("link")
        desc = i.get("description")
        msg += f"❍ [{title}]({link})\n**{desc}**\n\n"

    await webevent.edit_text(
        f"**Search Query:**\n`{query}`\n\n**Results:**\n{msg}",
        disable_web_page_preview=True,
    )


@pbot.on_message(filters.command("bimg"))
@subscribe
async def bingimg_search(_, message: Message):
    try:
        text = message.text.split(None, 1)[1]
    except IndexError:
        return await message.reply_text("Provide me a query to search!")

    search_message = await message.reply_text("🔎 Searching images on Bing...")

    url = "https://sugoi-api.vercel.app/bingimg?keyword=" + text
    images = await getreq(url)

    media = []
    for img in images[:7]:  # max 7 images
        media.append(InputMediaPhoto(media=img))

    await message.reply_media_group(media=media)
    await search_message.delete()


@pbot.on_message(filters.command("gimg"))
@subscribe
async def googleimg_search(_, message: Message):
    try:
        text = message.text.split(None, 1)[1]
    except IndexError:
        return await message.reply_text("Provide me a query to search!")

    search_message = await message.reply_text("🔎 Searching images on Google...")

    url = "https://sugoi-api.vercel.app/googleimg?keyword=" + text
    images = await getreq(url)

    media = []
    for img in images[:7]:  # max 7 images
        media.append(InputMediaPhoto(media=img))

    await message.reply_media_group(media=media)
    await search_message.delete()


@pbot.on_message(filters.command("img"))
async def img_search(_, message: Message):
    return await message.reply_text(
        "⚡ Command updated:\n\n/gimg → Google Image Search\n/bimg → Bing Image Search"
    )
