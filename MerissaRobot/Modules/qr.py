import base64
import requests
from pyrogram import filters
from MerissaRobot import pbot


# Available colors (add aur bhi kar sakte ho)
COLOR_MAP = {
    "red": "#FF0000",
    "blue": "#0000FF",
    "green": "#008000",
    "yellow": "#FFFF00",
    "black": "#000000",
    "white": "#FFFFFF",
    "purple": "#800080",
    "orange": "#FFA500",
    "pink": "#FFC0CB",
}


@pbot.on_message(filters.command(["q", "qu", "qt", "quote"]))
async def quote(client, m):
    qse = await m.reply_text("`Quoting..`")
    messages = []

    # --- User dict banane ka helper
    def create_user_dict(user):
        if user is None:
            return {}
        return {
            "id": user.id,
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "username": user.username,
            "language_code": "en",
            "title": f"{user.first_name or ''} {user.last_name or ''}",
            "photo": {
                "small_file_id": getattr(user.photo, "small_file_id", None),
                "small_file_unique_id": getattr(user.photo, "small_photo_unique_id", None),
                "big_file_id": getattr(user.photo, "big_file_id", None),
                "big_file_unique_id": getattr(user.photo, "big_photo_unique_id", None),
            } if user.photo else {},
            "type": "private",
            "name": f"{user.first_name or ''} {user.last_name or ''}",
        }

    # --- Background color detect karna
    bg_color = "#1b1429"  # default
    if len(m.command) > 1:
        col = m.command[1].lower()
        if col in COLOR_MAP:
            bg_color = COLOR_MAP[col]

    # --- Case 1: Reply + number of msgs
    if m.reply_to_message and len(m.command) > 1 and m.command[1].isdigit():
        num = m.reply_to_message.id
        for i in range(int(m.command[1])):
            mes = await client.get_messages(m.chat.id, num + i)
            uu = create_user_dict(mes.from_user)
            me = {
                "entities": [],
                "chatId": m.chat.id,
                "avatar": True,
                "from": uu,
                "text": mes.text,
                "replyMessage": {},
            }
            messages.append(me)

    # --- Case 2: Direct /q text
    elif (m.text.startswith(("/q ", "/qu ", "/qt ", "/quote "))) and (not m.reply_to_message):
        text_input = m.text.split(maxsplit=1)[1]
        me = {
            "entities": [],
            "chatId": m.chat.id,
            "avatar": True,
            "from": create_user_dict(m.from_user),
            "text": text_input,
        }
        messages.append(me)

    # --- Case 3: Reply to message only
    elif (m.text in ["/q", "/qu", "/qt", "/quote"]) and (m.reply_to_message):
        mes = m.reply_to_message
        uu = create_user_dict(mes.from_user)
        if mes.reply_to_message:  # quoted reply
            reply_message = {
                "text": mes.reply_to_message.text,
                "name": mes.reply_to_message.from_user.first_name,
                "chatId": mes.reply_to_message.from_user.id,
            }
            me = {
                "entities": [],
                "chatId": m.chat.id,
                "avatar": True,
                "from": uu,
                "text": mes.text,
                "replyMessage": reply_message,
            }
        else:
            me = {
                "entities": [],
                "chatId": m.chat.id,
                "avatar": True,
                "from": uu,
                "text": mes.text,
            }
        messages.append(me)

    else:
        await qse.edit("`Invalid usage. Reply to a text message or provide text with the command.`")
        return

    # --- API payload
    text = {
        "type": "quote",
        "format": "png",
        "backgroundColor": bg_color,
        "width": 512,
        "height": 768,
        "scale": 4,
        "messages": messages,
    }

    # --- Request to API
    try:
        r = requests.post("https://bot.lyo.su/quote/generate", json=text)
        response_data = r.json()
        image = response_data["result"]["image"]
        im = base64.b64decode(image.encode("utf-8"))
        open("qt.webp", "wb").write(im)
        await m.reply_sticker("qt.webp")
        await qse.delete()
    except Exception as e:
        await qse.edit(f"`Error occurred: {e}`")
