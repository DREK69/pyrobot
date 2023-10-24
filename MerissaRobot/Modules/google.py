from pyrogram import Client, filters
from pyrogram.types import InputMediaPhoto, Message

from MerissaRobot import pbot as app
from MerissaRobot.helpers import getreq, subscribe


@app.on_message(filters.command("google"))
async def google(client, message):
    userid = message.from_user.id
    sub = await subscribe(client, userid)
    if sub == False:
        return await message.reply_text(
            "Please Join @MerissaxUpdates to Use Premium Features"
        )
    if len(message.command) < 2:
        return await message.reply_text(
            "Give me some query to search on google\n\nex: /google who is merissarobot?"
        )
    webevent = await message.reply_text("Searching...")
    query = message.text.split(None, 1)[1]
    gresults = await getreq(f"https://api.princexd.tech/google?query={query}&limit=5")
    msg = ""
    for i in gresults["results"]:
        title = i["title"]
        link = i["link"]
        desc = i["description"]
        msg += f"❍[{title}]({link})\n**{desc}**\n\n"
    await webevent.edit_text(
        "**Search Query:**\n`" + query + "`\n\n**Results:**\n" + msg,
        disable_web_page_preview=True,
    )


@app.on_message(filters.command("bingimg"))
async def bingimg_search(client: Client, message: Message):
    userid = message.from_user.id
    sub = await subscribe(client, userid)
    if sub == False:
        return await message.reply_text(
            "Please Join @MerissaxUpdates to Use Premium Features"
        )
    try:
        text = message.text.split(None, 1)[1]
    except IndexError:
        return await message.reply_text("Provide me a query to search!")

    search_message = await message.reply_text("Searching image using Bing search 🔎")

    url = "https://sugoi-api.vercel.app/bingimg?keyword=" + text
    images = await getreq(url)
    media = []
    count = 0
    for img in images:
        if count == 7:
            break

        media.append(InputMediaPhoto(media=img))
        count += 1

    await message.reply_media_group(media=media)
    await search_message.delete()


@app.on_message(filters.command("googleimg"))
async def googleimg_search(client: Client, message: Message):
    userid = message.from_user.id
    sub = await subscribe(client, userid)
    if sub == False:
        return await message.reply_text(
            "Please Join @MerissaxUpdates to Use Premium Features"
        )
    try:
        text = message.text.split(None, 1)[1]
    except IndexError:
        return await message.reply_text("Provide me a query to search!")

    search_message = await message.reply_text("Searching image using Google search 🔎")

    url = "https://sugoi-api.vercel.app/googleimg?keyword=" + text
    images = await getreq(url)
    media = []
    count = 0
    for img in images:
        if count == 7:
            break

        media.append(InputMediaPhoto(media=img))
        count += 1

    await message.reply_media_group(media=media)
    await search_message.delete()


@app.on_message(filters.command("img"))
async def img_search(client: Client, message: Message):
    return await message.reply_text("Command /img changed:\n\n/gimg: For Google Image Search\n/bimg: For Bing Image Search")
