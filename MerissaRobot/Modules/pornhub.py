import asyncio
import os

import youtube_dl
from pornhub_api import PornhubApi
from pornhub_api.backends.aiohttp import AioHttpBackend
from pyrogram import filters
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Message,
)
from youtube_dl.utils import DownloadError

from MerissaRobot import pbot as Client

if os.path.exists("downloads"):
    print("✅ File is exist")
else:
    print("✅ File has made")


active = []
queues = []


async def run_async(func, *args, **kwargs):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, func, *args, **kwargs)


def url(filter, client, update):
    if "www.pornhub" in update.text:
        return True
    else:
        return False


url_filter = filters.create(url, name="url_filter")


@Client.on_inline_query()
async def inline_search(c: Client, q: InlineQuery):
    query = q.query
    backend = AioHttpBackend()
    api = PornhubApi(backend=backend)
    results = []
    try:
        src = await api.search.search(query)
    except ValueError:
        results.append(
            InlineQueryResultArticle(
                title="I can't found it!",
                description="The video can't be found, try again later.",
                input_message_content=InputTextMessageContent(
                    message_text="Video not found!"
                ),
            ),
        )
        await q.answer(
            results,
            switch_pm_text="• Results •",
            switch_pm_parameter="start",
        )

        return

    videos = src.videos
    await backend.close()

    for vid in videos:
        try:
            pornstars = ", ".join(v for v in vid.pornstars)
            categories = ", ".join(v for v in vid.categories)
            tags = ", #".join(v for v in vid.tags)
        except:
            pornstars = "N/A"
            categories = "N/A"
            tags = "N/A"
        capt = (
            f"Title: `{vid.title}`\n"
            f"Duration: `{vid.duration}`\n"
            f"Views: `{vid.views}`\n\n"
            f"**{pornstars}**\n"
            f"Category: {categories}\n\n"
            f"{tags}"
            f"Link: {vid.url}"
        )

        text = f"{vid.url}"

        results.append(
            InlineQueryResultArticle(
                title=vid.title,
                input_message_content=InputTextMessageContent(
                    message_text=text,
                    disable_web_page_preview=True,
                ),
                description=f"Duration: {vid.duration}\nViews: {vid.views}\nRating: {vid.rating}",
                thumb_url=vid.thumb,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("Watch in web", url=vid.url),
                        ],
                    ],
                ),
            ),
        )

    await q.answer(
        results,
        switch_pm_text="• Results •",
        switch_pm_parameter="start",
    )


@Client.on_message(url_filter)
async def options(c: Client, m: Message):
    await m.reply_text(
        "Tap the button to continue action!",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Download",
                        callback_data=f"d_{m.text}",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Watch in web",
                        url=m.text,
                    ),
                ],
            ],
        ),
    )


@Client.on_callback_query(filters.regex("^d"))
async def get_video(c: Client, q: CallbackQuery):
    url = q.data.split("_", 1)[1]
    msg = await q.message.edit(
        "Downloading and Uploading Speed could be slow Plase wait..."
    )
    user_id = q.message.from_user.id

    if "some" in active:
        await q.message.edit("Sorry, you can only download videos at a time!")
        return
    else:
        active.append(user_id)

    opts = {
        "format": "best",
        "addmetadata": True,
        "key": "FFmpegMetadata",
        "prefer_ffmpeg": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "postprocessors": [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}],
        "outtmpl": "%(id)s.mp4",
        "logtostderr": False,
        "quiet": True,
    }
    with youtube_dl.YoutubeDL(opts) as ydl:
        try:
            await run_async(ydl.download, [url])
        except DownloadError:
            await q.message.edit("Sorry, an error occurred")
            return

    for file in os.listdir("."):
        if file.endswith(".mp4"):
            await Client.send_video(
                -1001708378054,
                f"{file}",
                width=1280,
                height=720,
                caption="The content you requested has been successfully downloaded!",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "• Donate •", url="https://t.me/princexdonatebot"
                            ),
                        ],
                    ],
                ),
            )
            os.remove(f"{file}")
            break
        else:
            continue
    await q.message.reply_text("Join Here - https://t.me/+Ow7dStIJSLViY2Y1")
    await msg.delete()
    active.remove(user_id)
