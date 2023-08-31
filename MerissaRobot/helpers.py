import mutagen
import requests


def save_file(url, name):
    with open(name, "wb") as f:
        f.write(requests.get(url).content)
    return name


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
