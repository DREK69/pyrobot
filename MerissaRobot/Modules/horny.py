import random
import time

from pyrogram import filters
from pyrogram.types import *

from MerissaRobot import pbot as bot
from MerissaRobot import telethn as asst
from MerissaRobot.helpers import getreq


@bot.on_message(filters.command("wish"))
async def wish(_, m):
    if len(m.command) < 2:
        await m.reply("😉 ~~**Add~~ wish!**")
        return
    api = await getreq("https://nekos.best/api/v2/happy")
    url = api["results"][0]["url"]
    text = m.text.split(None, 1)[1]
    wish_count = random.randint(1, 100)
    wish = f"✨~~ **hey! {m.from_user.first_name}!** ~~🤗"
    wish += f"✨ ~~**Your wish**:~~ **{text}** 😃"
    wish += f"✨ ~~ **Possible to: {wish_count}%** ~~"
    file_id = (
        "CAACAgIAAx0CXss_8QABBpFuYrMigIRzrvu0BLalDGPgfyhzqNsAAgIVAAI6wVBJt0ySCb_oqBMeBA"
    )
    msg = await m.reply_sticker(file_id)
    time.sleep(2)
    await msg.delete()
    await m.reply_animation(
        url,
        caption=(wish),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "❓ What is This", url="https://t.me/vegetaUpdates/175"
                    )
                ]
            ]
        ),
    )


BUTTON = InlineKeyboardMarkup([[InlineKeyboardButton(text="❓ What Is This", url="https://t.me/MerissaxUpdates")]])
HOT = "https://telegra.ph/file/daad931db960ea40c0fca.gif"
SMEXY = "https://telegra.ph/file/a23e9fd851fb6bc771686.gif"
LEZBIAN = "https://telegra.ph/file/5609b87f0bd461fc36acb.gif"
BIGBALL = "https://i.gifer.com/8ZUg.gif"
LANG = "https://telegra.ph/file/423414459345bf18310f5.gif"
CUTIE = "https://64.media.tumblr.com/d701f53eb5681e87a957a547980371d2/tumblr_nbjmdrQyje1qa94xto1_500.gif"


@bot.on_message(filters.command("horny"))
async def horny(_, message):
    reply = message.reply_to_message
    if not reply:
        user_id = message.from_user.id
        user_name = message.from_user.first_name
        mention = f"[{user_name}](tg://user?id={str(user_id)})"
        mm = random.randint(1, 100)
        HORNY = f"**🔥** {mention} **Is** {mm}**% Horny!**"
        await message.reply_text(HOT, caption=HORNY, reply_markup=BUTTON)
    if reply:
        id = reply.id
        name = reply.first_name
        mention = f"[{name}](tg://user?id={str(id)})"
        mm = random.randint(1, 100)
        HORNY = f"**🔥** {mention} **Is** {mm}**% Horny!**"
        await message.reply_video(HOT, caption=HORNY, reply_markup=BUTTON)


@bot.on_message(filters.command("gay"))
async def gay(_, message):
    reply = message.reply_to_message
    if not reply:
        user_id = message.from_user.id
        user_name = message.from_user.first_name
        mention = f"[{user_name}](tg://user?id={str(user_id)})"
        mm = random.randint(1, 100)
        GAY = f"**🏳‍🌈** {mention} **Is** {mm}**% Gay!**"
        await message.reply_video(SMEXY, caption=GAY, buttons=BUTTON)
    if reply:
        id = reply.id
        name = reply.first_name
        mention = f"[{name}](tg://user?id={str(id)})"
        mm = random.randint(1, 100)
        GAY = f"**🏳‍🌈** {mention} **Is** {mm}**% Gay!**"
        await message.reply_video(SMEXY, caption=GAY, reply_markup=BUTTON)


@bot.on_message(filters.command("lezbian"))
async def lezbian(_, message):
    reply = message.reply_to_message
    if not reply:
        user_id = message.from_user.id
        user_name = message.from_user.first_name
        mention = f"[{user_name}](tg://user?id={str(user_id)})"
        mm = random.randint(1, 100)
        FEK = f"**💜** {mention} **Is** {mm}**% Lezbian!**"
        await message.reply_video(LEZBIAN, caption=FEK, reply_markup=BUTTON)
    if reply:
        id = reply.id
        name = reply.first_name
        mention = f"[{name}](tg://user?id={str(id)})"
        mm = random.randint(1, 100)
        FEK = f"**💜** {mention} **Is** {mm}**% Lezbian!**"
        await e.reply(LEZBIAN, caption=FEK, reply_markup=BUTTON)


@bot.on_message(filters.command("boobs"))
async def boobs(_, message):
    reply = message.reply_to_message
    if not reply:
        user_id = message.from_user.id
        user_name = message.from_user.first_name
        mention = f"[{user_name}](tg://user?id={str(user_id)})"
        mm = random.randint(1, 100)
        BOOBS = f"**🍒** {mention}**'s Boobs Size Is** {mm}**!**"
        await message.reply_video(BIGBALL, caption=BOOBS, reply_markup=BUTTON)
    if reply:
        id = reply.id
        name = reply.first_name
        mention = f"[{name}](tg://user?id={str(id)})"
        mm = random.randint(1, 100)
        BOOBS = f"**🍒** {mention}**'s Boobs Size Is** {mm}**!**"
        await message.reply_video(BIGBALL, caption=BOOBS, reply_markup=BUTTON)


@bot.on_message(filters.command("cock"))
async def cock(_, message):
    reply = message.reply_to_message
    if not reply:
        user_id = message.from_user.id
        user_name = message.from_user.first_name
        mention = f"[{user_name}](tg://user?id={str(user_id)})"
        mm = random.randint(1, 100)
        COCK = f"**🍆** {mention}**'s Cock Size Is** {mm}**cm**"
        await message.reply_video(LANG, caption=COCK, reply_markup=BUTTON)
    if reply:
        id = reply.id
        name = reply.first_name
        mention = f"[{name}](tg://user?id={str(id)})"
        mm = random.randint(1, 100)
        COCK = f"**🍆** {mention}**'s Cock Size Is** {mm}**mm**"
        await message.reply_video(LANG, caption=COCK, reply_markup=BUTTON)


@bot.on_message(filters.command("cute"))
async def cute(_, message):
    reply = message.reply_to_message
    if not reply:
        user_id = message.from_user.id
        user_name = message.from_user.first_name
        mention = f"[{user_name}](tg://user?id={str(user_id)})"
        mm = random.randint(1, 100):
        CUTE = f"**🍑** {mention} {mm}**% Cute**"
        await message.reply_video(CUTIE, caption=CUTE, reply_markup=BUTTON)
    if reply:
        id = reply.id
        name = reply.first_name
        mention = f"[{name}](tg://user?id={str(id)})"
        mm = random.randint(1, 100)
        CUTE = f"**🍑** {mention} {mm}**% Cute**"
        await message.reply_video(CUTIE, caption=CUTE, reply_markup=BUTTON)


@bot.on_message(filters.command("boob"))
async def boobs(client, message):
    pic = await getreq("https://api.princexd.tech/boobs")
    await client.send_photo(
        message.chat.id,
        pic,
        caption="Powered By @MerissaRobot",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Change 🔂",
                        callback_data="boob",
                    ),
                ],
            ],
        ),
    )


@bot.on_message(filters.command("animepfp"))
async def animepfp(client, message):
    pic = await getreq("https://api.princexd.tech/animepfp")
    await client.send_photo(
        message.chat.id,
        pic["url"],
        caption="Powered By @MerissaRobot",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Change 🔂",
                        callback_data="animepfp",
                    ),
                ],
            ],
        ),
    )
