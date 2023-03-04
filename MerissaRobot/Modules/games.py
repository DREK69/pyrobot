from pyrogram import filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from MerissaRobot import pbot as app

sologame = ReplyKeyboardMarkup(
    [
        ["▶️ Play - Subway Surf", "▶️ Play - Temple Run 2"],
        ["▶️ Play - Uno Multi-Player", "▶️ Play - Stickmen Hook"],
        ["▶️ Play - Stickmen Climb 2", "▶️ Play - Tunnel Rush"],
        ["▶️ Play - Murder", "▶️ Play - Car Race"],
        ["🔙 Back", "Close 🗑"],
    ],
    resize_keyboard=True,
)

categories = ReplyKeyboardMarkup(
    [
        ["⭐ Featured", "🕹 Arcade"],
        ["⚽ Sport", "🥊 Action"],
        ["🌀 Puzzle", "💥 Quickies"],
        ["🛀 Relax", "🏎️ Racing"],
        ["🤪 Crazy", "🔙 Back"],
    ],
    resize_keyboard=True,
)

game = ReplyKeyboardMarkup(
    [
        ["🎮 Play Solo", "👫 Play With Friends"],
        ["🔥 Trending games", "🎮 Categories"],
        ["Close 🗑"],
    ],
    resize_keyboard=True,
)

delete = ReplyKeyboardRemove()


@app.on_message(filters.command("games") & filters.private)
async def gamescmd(_, message: Message):
    chat = message.from_user.id
    await app.send_photo(
        chat_id=chat,
        photo="https://te.legra.ph/file/98a2330097ec25a078b95.jpg",
        caption="Hello Dear, Welcome to Merissa Gamezone. We have attched some games for you, Press the button and Play Games.",
        reply_markup=game,
    )


@app.on_message(filters.private & filters.regex(pattern="🔥 Trending games"))
async def games(_, message: Message):
    chat = message.from_user.id
    await app.send_message(
        chat_id=chat,
        text="Hello Dear, You can play Games here no Need to download anything, press the button below and play games.",
        reply_markup=sologame,
    )


@app.on_message(filters.private & filters.regex(pattern="🎮 Play Solo"))
async def games(_, message: Message):
    chat = message.from_user.id
    await app.send_message(
        chat_id=chat,
        text="Hello Dear, You can play Games here no Need to download anything, press the button below and play games.",
        reply_markup=sologame,
    )


@app.on_message(filters.private & filters.regex(pattern="🎮 Categories"))
async def games(_, message: Message):
    chat = message.from_user.id
    await app.send_message(
        chat_id=chat,
        text="Hello Dear, You can play Games here no Need to download anything, press the button below and play games.",
        reply_markup=categories,
    )


@app.on_message(filters.private & filters.regex(pattern="▶️ Play - Subway Surf"))
async def games(_, message: Message):
    chat = message.from_user.id
    text = """🎮 Name - Subway Surfers"""
    img = "https://telegra.ph/file/bab42e80fa20b8d680727.jpg"
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Play Game 🎮", url="https://poki.com/en/g/subway-surfers"
                ),
            ],
        ]
    )
    await app.send_photo(chat_id=chat, photo=img, caption=text, reply_markup=button)


@app.on_message(filters.private & filters.regex(pattern="▶️ Play - Murder"))
async def games(_, message: Message):
    chat = message.from_user.id
    text = """🎮 Name - Murder"""
    img = "https://telegra.ph/file/674a11eb6c45484a80d96.jpg"
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Play Game 🎮", url="https://poki.com/en/g/murder"),
            ],
        ]
    )
    await app.send_photo(chat_id=chat, photo=img, caption=text, reply_markup=button)


@app.on_message(filters.private & filters.regex(pattern="▶️ Play - Tunnel Rush"))
async def games(_, message: Message):
    chat = message.from_user.id
    text = """🎮 Name - Tunnel Rush"""
    img = "https://telegra.ph/file/98b0acefc6b313214775a.jpg"
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Play Game 🎮", url="https://poki.com/en/g/tunnel-rush"
                ),
            ],
        ]
    )
    await app.send_photo(chat_id=chat, photo=img, caption=text, reply_markup=button)


@app.on_message(filters.private & filters.regex(pattern="▶️ Play - Car Race"))
async def games(_, message: Message):
    chat = message.from_user.id
    text = """🎮 Name - Car Race"""
    img = "https://telegra.ph/file/b717ec6b5d937fc2a7673.jpg"
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Play Game 🎮",
                    url="https://poki.com/en/g/grand-prix-hero",
                ),
            ],
        ]
    )
    await app.send_photo(chat_id=chat, photo=img, caption=text, reply_markup=button)


@app.on_message(filters.private & filters.regex(pattern="▶️ Play - Stickmen Hook"))
async def games(_, message: Message):
    chat = message.from_user.id
    text = """🎮 Name - Stickmen Hook"""
    img = "https://telegra.ph/file/133b529fa2b8dc316cfd1.jpg"
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Play Game 🎮", url="https://poki.com/en/g/stickman-hook"
                ),
            ],
        ]
    )
    await app.send_photo(chat_id=chat, photo=img, caption=text, reply_markup=button)


@app.on_message(filters.private & filters.regex(pattern="▶️ Play - Chess Master"))
async def games(_, message: Message):
    chat = message.from_user.id
    text = """🎮 Name - Chess Master"""
    img = "https://telegra.ph/file/41b9d9ffddad73bd64e89.jpg"
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Play Game 🎮", url="https://poki.com/en/g/master-chess"
                ),
            ],
        ]
    )
    await app.send_photo(chat_id=chat, photo=img, caption=text, reply_markup=button)


@app.on_message(filters.private & filters.regex(pattern="▶️ Play - Uno Multi-Player"))
async def games(_, message: Message):
    chat = message.from_user.id
    text = """🎮 Name - Uno Multi-Player Game"""
    img = "https://telegra.ph/file/c4be56a3fdde4d880a918.jpg"
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Play Game 🎮", url="https://poki.com/en/g/uno-online"
                ),
            ],
        ]
    )
    await app.send_photo(chat_id=chat, photo=img, caption=text, reply_markup=button)


@app.on_message(filters.private & filters.regex(pattern="▶️ Play - Stickmen Climb 2"))
async def games(_, message: Message):
    chat = message.from_user.id
    text = """🎮 Name - Stickmen Climb 2"""
    img = "https://telegra.ph/file/1c8c4a71d48075a144b32.jpg"
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Play Game 🎮",
                    url="https://poki.com/en/g/stickman-climb-2",
                ),
            ],
        ]
    )
    await app.send_photo(chat_id=chat, photo=img, caption=text, reply_markup=button)


@app.on_message(filters.private & filters.regex(pattern="▶️ Play - Temple Run 2"))
async def games(_, message: Message):
    chat = message.from_user.id
    text = """🎮 Name - Temple Run 2"""
    img = "https://telegra.ph/file/e061a91b4dcc4db71c004.jpg"
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Play Game 🎮", url="https://poki.com/en/g/temple-run-2"
                ),
            ],
        ]
    )
    await app.send_photo(chat_id=chat, photo=img, caption=text, reply_markup=button)


@app.on_message(filters.private & filters.regex(pattern="🔙 Back"))
async def back(_, message: Message):
    chat = message.from_user.id
    await app.send_message(
        chat_id=chat,
        text="Welcome To Main Menu Click Below Button to Play Games",
        reply_markup=game,
    )


@app.on_message(filters.private & filters.regex(pattern="Close 🗑"))
async def back(_, message: Message):
    chat = message.from_user.id
    await app.send_message(
        chat_id=chat,
        text="Keyboard is Closed ❌. Press /games to Get Keyboard",
        reply_markup=delete,
    )


@app.on_message(filters.command("dice"))
async def throw_dice(client, message: Message):
    await client.send_dice(message.chat.id, "🎲")


@app.on_message(filters.command("dart"))
async def throw_dice(client, message: Message):
    await client.send_dice(message.chat.id, "🎯")


@app.on_message(filters.command("basket"))
async def throw_dice(client, message: Message):
    await client.send_dice(message.chat.id, "🏀")


@app.on_message(filters.command("bowling"))
async def throw_dice(client, message: Message):
    await client.send_dice(message.chat.id, "🎳")


@app.on_message(filters.command("football"))
async def throw_dice(client, message: Message):
    await client.send_dice(message.chat.id, "⚽")


@app.on_message(filters.command("slot"))
async def throw_dice(client, message: Message):
    await client.send_dice(message.chat.id, "🎰")


__mod_name__ = "Games 🎮"

__help__ = """
*Play Games Online*:
- /games : To get all Games

*Play Game With Emojis:*
/dice - Dice 🎲
/dart - Dart 🎯
/basket - Basket Ball 🏀
/bowling - Bowling Ball 🎳
/football - Football ⚽
/slot - Spin slot machine 🎰"""
