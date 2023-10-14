import os
from configparser import ConfigParser

from pyrogram import Client, filters, types
from shazamio import FactoryArtist, FactoryTrack, Shazam, exceptions

from MerissaRobot import pbot

shazam = Shazam()

    
async def recognize(path):
    return await shazam.recognize_song(path)

async def related(track_id):
    try:
        return (
            await shazam.related_tracks(track_id=track_id, limit=50, start_from=2)
        )["tracks"]
    except exceptions.FailedDecodeJson:
        return None

async def get_artist(query: str):
    artists = await shazam.search_artist(query=query, limit=50)
    hits = []
    try:
        for artist in artists["artists"]["hits"]:
            hits.append(FactoryArtist(artist).serializer())
        return hits
    except KeyError:
        return None

async def get_artist_tracks(artist_id: int):
    tracks = []
    tem = (await shazam.artist_top_tracks(artist_id=artist_id, limit=50))["tracks"]
    try:
        for track in tem:
            tracks.append(FactoryTrack(data=track).serializer())
        return tracks
    except KeyError:
        return None


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
            types.InlineKeyboardButton("🎵 Listen", url=f'{r["url"]}')
        ],
    ]
    await message.reply_photo(
        r["images"]["coverarthq"],
        caption=out,
        reply_markup=types.InlineKeyboardMarkup(buttons),
    )
