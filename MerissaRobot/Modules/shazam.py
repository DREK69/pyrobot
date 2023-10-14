import os
from configparser import ConfigParser

from pyrogram import Client, filters, types
from shazamio import FactoryArtist, FactoryTrack, Shazam, exceptions

shazam = Shazam()


class bot(Client):
    def __init__(self, name):
        config_file = f"{name}.ini"
        config = ConfigParser()
        config.read(config_file)
        name = name.lower()
        plugins = {"root": os.path.join(__package__, "plugins")}
        api_id = config.get("pyrogram", "api_id")
        api_hash = config.get("pyrogram", "api_hash")
        super().__init__(
            name,
            api_id=api_id,
            api_hash=api_hash,
            config_file=config_file,
            workers=16,
            plugins=plugins,
            workdir="./",
        )

    async def start(self):
        await super().start()
        print("bot started. Hi.")

    async def stop(self, *args):
        await super().stop()
        print("bot stopped. Bye.")

    async def recognize(self, path):
        return await shazam.recognize_song(path)

    async def related(self, track_id):
        try:
            return (
                await shazam.related_tracks(track_id=track_id, limit=50, start_from=2)
            )["tracks"]
        except exceptions.FailedDecodeJson:
            return None

    async def get_artist(self, query: str):
        artists = await shazam.search_artist(query=query, limit=50)
        hits = []
        try:
            for artist in artists["artists"]["hits"]:
                hits.append(FactoryArtist(artist).serializer())
            return hits
        except KeyError:
            return None

    async def get_artist_tracks(self, artist_id: int):
        tracks = []
        tem = (await shazam.artist_top_tracks(artist_id=artist_id, limit=50))["tracks"]
        try:
            for track in tem:
                tracks.append(FactoryTrack(data=track).serializer())
            return tracks
        except KeyError:
            return None


@bot.on_message(filters.audio | filters.video | filters.voice)
async def voice_handler(_, message):
    file_size = message.audio or message.video or message.voice
    if 30641629 < file_size.file_size:
        await message.reply_text("**⚠️ Max file size has been reached.**")
        return
    file = await message.download(f"{bot.rnd_id()}.mp3")
    r = (await bot.recognize(file)).get("track", None)
    os.remove(file)
    if r is None:
        await message.reply_text("**⚠️ Cannot recognize the audio**")
        return
    out = f'**Title**: `{r["title"]}`\n'
    out += f'**Artist**: `{r["subtitle"]}`\n'
    buttons = [
        [
            types.InlineKeyboardButton(
                "🎼 Related Songs",
                switch_inline_query_current_chat=f'related {r["key"]}',
            ),
            types.InlineKeyboardButton("🔗 Share", url=f'{r["share"]["html"]}'),
        ],
        [types.InlineKeyboardButton("🎵 Listen", url=f'{r["url"]}')],
    ]
    response = r.get("artists", None)
    if response:
        buttons.append(
            [
                types.InlineKeyboardButton(
                    f'💿 More Tracks from {r["subtitle"]}',
                    switch_inline_query_current_chat=f'tracks {r["artists"][0]["id"]}',
                )
            ]
        )
    await message.reply_photo(
        r["images"]["coverarthq"],
        caption=out,
        reply_markup=types.InlineKeyboardMarkup(buttons),
    )
