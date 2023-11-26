import re

from ytmusicapi import YTMusic

ytmusic = YTMusic()


def getvideoid(link):
    pattern = re.compile(
        r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    )
    match = pattern.search(link)
    videoid = match.group(1)
    return videoid


def ytmsearch(query):
    if "https" in query:
        videoid = getvideoid(link)
        result = ytmusic.get_song(videoid)
    else:
        result = ytmusic.search(query, filter="songs", limit=10)
    return {"results": result}
