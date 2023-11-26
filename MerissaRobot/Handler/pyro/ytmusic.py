from ytmusicapi import YTMusic

ytmusic = YTMusic()


async def ytmusicapi(query):
    result = ytmusic.search(query, filter="songs", limit=10)
    return {"results": result}

def ytmusicapi(videoid):
    result = ytmusic.get_song(videoid)
    return {"results": result}
