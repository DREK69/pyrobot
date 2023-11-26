from ytmusicapi import YTMusic

ytmusic = YTMusic()


async def ytmsearch(query):
    result = ytmusic.search(query, filter="songs", limit=10)
    return {"results": result}


def ytmtrack(videoid):
    result = ytmusic.get_song(videoid)
    return {"results": result}
