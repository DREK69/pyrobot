import asyncio
import os
import random
import time
import urllib

import requests
from pyrogram import filters
from pyrogram.types import *
from telethon import Button, events

from MerissaRobot import TEMP_DOWNLOAD_DIRECTORY
from MerissaRobot import pbot as bot
from MerissaRobot import telethn as asst


@bot.on_message(filters.command("wish"))
async def wish(_, m):
    if len(m.command) < 2:
        await m.reply("😉 ~~**Add~~ wish!**")
        return
    api = requests.get("https://nekos.best/api/v2/happy").json()
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


BUTTON = [[Button.url("❓ What Is This", "https://t.me/vegetaUpdates/173")]]
HOT = "https://telegra.ph/file/daad931db960ea40c0fca.gif"
SMEXY = "https://telegra.ph/file/a23e9fd851fb6bc771686.gif"
LEZBIAN = "https://telegra.ph/file/5609b87f0bd461fc36acb.gif"
BIGBALL = "https://i.gifer.com/8ZUg.gif"
LANG = "https://telegra.ph/file/423414459345bf18310f5.gif"
CUTIE = "https://64.media.tumblr.com/d701f53eb5681e87a957a547980371d2/tumblr_nbjmdrQyje1qa94xto1_500.gif"


@asst.on(events.NewMessage(pattern="/horny ?(.*)"))
async def horny(e):
    if not e.is_reply:
        user_id = e.sender.id
        user_name = e.sender.first_name
        mention = f"[{user_name}](tg://user?id={str(user_id)})"
        mm = random.randint(1, 100)
        HORNY = f"**🔥** {mention} **Is** {mm}**% Horny!**"
        await e.reply(HORNY, buttons=BUTTON, file=HOT)
    if e.is_reply:
        replied = await e.get_reply_message()
        id = replied.sender.id
        name = replied.sender.first_name
        mention = f"[{name}](tg://user?id={str(id)})"
        mm = random.randint(1, 100)
        HORNY = f"**🔥** {mention} **Is** {mm}**% Horny!**"
        await e.reply(HORNY, buttons=BUTTON, file=HOT)


@asst.on(events.NewMessage(pattern="/gay ?(.*)"))
async def gay(e):
    if not e.is_reply:
        user_id = e.sender.id
        user_name = e.sender.first_name
        mention = f"[{user_name}](tg://user?id={str(user_id)})"
        mm = random.randint(1, 100)
        GAY = f"**🏳‍🌈** {mention} **Is** {mm}**% Gay!**"
        await e.reply(GAY, buttons=BUTTON, file=SMEXY)
    if e.is_reply:
        replied = await e.get_reply_message()
        id = replied.sender.id
        name = replied.sender.first_name
        mention = f"[{name}](tg://user?id={str(id)})"
        mm = random.randint(1, 100)
        GAY = f"**🏳‍🌈** {mention} **Is** {mm}**% Gay!**"
        await e.reply(GAY, buttons=BUTTON, file=SMEXY)


@asst.on(events.NewMessage(pattern="/lezbian ?(.*)"))
async def lezbian(e):
    if not e.is_reply:
        user_id = e.sender.id
        user_name = e.sender.first_name
        mention = f"[{user_name}](tg://user?id={str(user_id)})"
        mm = random.randint(1, 100)
        FEK = f"**💜** {mention} **Is** {mm}**% Lezbian!**"
        await e.reply(FEK, buttons=BUTTON, file=LEZBIAN)
    if e.is_reply:
        replied = await e.get_reply_message()
        id = replied.sender.id
        name = replied.sender.first_name
        mention = f"[{name}](tg://user?id={str(id)})"
        mm = random.randint(1, 100)
        FEK = f"**💜** {mention} **Is** {mm}**% Lezbian!**"
        await e.reply(FEK, buttons=BUTTON, file=LEZBIAN)


@asst.on(events.NewMessage(pattern="/boobs ?(.*)"))
async def boobs(e):
    if not e.is_reply:
        user_id = e.sender.id
        user_name = e.sender.first_name
        mention = f"[{user_name}](tg://user?id={str(user_id)})"
        mm = random.randint(1, 100)
        BOOBS = f"**🍒** {mention}**'s Boobs Size Is** {mm}**!**"
        await e.reply(BOOBS, buttons=BUTTON, file=BIGBALL)
    if e.is_reply:
        replied = await e.get_reply_message()
        id = replied.sender.id
        name = replied.sender.first_name
        mention = f"[{name}](tg://user?id={str(id)})"
        mm = random.randint(1, 100)
        BOOBS = f"**🍒** {mention}**'s Boobs Size Is** {mm}**!**"
        await e.reply(BOOBS, buttons=BUTTON, file=BIGBALL)


@asst.on(events.NewMessage(pattern="/cock ?(.*)"))
async def cock(e):
    if not e.is_reply:
        user_id = e.sender.id
        user_name = e.sender.first_name
        mention = f"[{user_name}](tg://user?id={str(user_id)})"
        mm = random.randint(1, 100)
        COCK = f"**🍆** {mention}**'s Cock Size Is** {mm}**cm**"
        await e.reply(COCK, buttons=BUTTON, file=LANG)
    if e.is_reply:
        replied = await e.get_reply_message()
        id = replied.sender.id
        name = replied.sender.first_name
        mention = f"[{name}](tg://user?id={str(id)})"
        mm = random.randint(1, 100)
        COCK = f"**🍆** {mention}**'s Cock Size Is** {mm}**mm**"
        await e.reply(COCK, buttons=BUTTON, file=LANG)


@asst.on(events.NewMessage(pattern="/cute ?(.*)"))
async def cute(e):
    if not e.is_reply:
        user_id = e.sender.id
        user_name = e.sender.first_name
        mention = f"[{user_name}](tg://user?id={str(user_id)})"
        mm = random.randint(1, 100)
        CUTE = f"**🍑** {mention} {mm}**% Cute**"
        await e.reply(CUTE, buttons=BUTTON, file=CUTIE)
    if e.is_reply:
        replied = await e.get_reply_message()
        id = replied.sender.id
        name = replied.sender.first_name
        mention = f"[{name}](tg://user?id={str(id)})"
        mm = random.randint(1, 100)
        CUTE = f"**🍑** {mention} {mm}**% Cute**"
        await e.reply(CUTE, buttons=BUTTON, file=CUTIE)


@bot.on_message(filters.command("boob"))
async def boobs(client, message):
    if not os.path.isdir(TEMP_DOWNLOAD_DIRECTORY):
        os.makedirs(TEMP_DOWNLOAD_DIRECTORY)
    pic_loc = os.path.join(TEMP_DOWNLOAD_DIRECTORY, "bobs.jpg")
    a = await message.reply_text("📥 Downloading")
    await asyncio.sleep(0.5)
    await a.edit("📤 Uploading")
    nsfw = requests.get("http://api.oboobs.ru/noise/1").json()[0]["preview"]
    urllib.request.urlretrieve("http://media.oboobs.ru/{}".format(nsfw), pic_loc)
    await client.send_photo(
        message.chat.id,
        pic_loc,
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
    os.remove(pic_loc)
    await a.delete()


@bot.on_callback_query(filters.regex("boob"))
async def memess(_, query: CallbackQuery):
    res = requests.get("https://api.prince-xd.ml/boobs").json()
    await query.edit_message_media(
        InputMediaPhoto(res)
    )
