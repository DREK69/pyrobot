import aiofiles
import aiohttp
import mutagen
import requests
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant

from MerissaRobot import FORCE_CHANNEL


async def save_file(url, filename):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                f = await aiofiles.open(filename, mode="wb")
                await f.write(await resp.read())
                await f.close()
    return filename


async def getreq(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            try:
                data = await resp.json()
            except:
                data = await resp.text()
    return data


async def postreq(url, data):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as resp:
            try:
                data = await resp.json()
            except:
                data = await resp.text()
    return data


def subscribe(func):
    async def non_subscribe(client, message):
        user_id = message.from_user.id
        try:
            member = await client.get_chat_member(
                chat_id=FORCE_CHANNEL, user_id=user_id
            )
            return await func(client, message)
        except UserNotParticipant:
            return await message.reply_photo(
                photo="https://te.legra.ph/file/2b3a7af1d01513c032739.jpg",
                caption="Join our Telegram Update Channel @MerissaxUpdates to Get Premium for free in MerissaRobot",
            )

    return non_subscribe


async def get_ytthumb(videoid: str):
    thumb_quality = [
        "hq720.jpg",  # Best quality
        "hqdefault.jpg",
        "sddefault.jpg",
        "mqdefault.jpg",
        "default.jpg",  # Worst quality
    ]
    thumb_link = "https://i.imgur.com/4LwPLai.png"
    for qualiy in thumb_quality:
        link = f"https://i.ytimg.com/vi/{videoid}/{qualiy}"
        if (requests.get(link)).status_code == 200:
            thumb_link = link
            break
    return thumb_link


def embed_album_art(cover_filepath, filepath):
    with open(cover_filepath, "rb") as f:
        cover_data = f.read()
    mf = mutagen.File(filepath)
    if isinstance(mf.tags, mutagen.mp4.MP4Tags) or isinstance(mf, mutagen.mp4.MP4):
        mf["covr"] = [
            mutagen.mp4.MP4Cover(cover_data, imageformat=mutagen.mp4.AtomDataType.JPEG)
        ]
    else:
        picture = mutagen.flac.Picture()
        picture.type = 3
        picture.data = cover_data
        picture.desc = "front cover"
        mf.add_picture(picture)
    mf.save()
