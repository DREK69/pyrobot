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
