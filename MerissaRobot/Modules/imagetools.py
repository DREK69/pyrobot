import os
import textwrap
from inspect import getfullargspec

import cv2
from PIL import Image, ImageDraw, ImageFont
from pyrogram import filters
from pyrogram.types import Message
from telegraph import upload_file

from MerissaRobot import pbot
from MerissaRobot.helpers import subscribe


@pbot.on_message(filters.command("ocr") & filters.private)
@subscribe
async def movie(client, message):
    reply = message.reply_to_message.photo
    if reply:
        m = await message.reply_text("Please wait...")
        download_location = await client.download_media(reply)
        x = upload_file(download_location)[0]
        imglink = "https://te.legra.ph" + x
        os.remove(download_location)
        ocr = await getreq(
            f"https://script.google.com/macros/s/AKfycbwURISN0wjazeJTMHTPAtxkrZTWTpsWIef5kxqVGoXqnrzdLdIQIfLO7jsR5OQ5GO16/exec?url={imglink}"
        )
        text = ocr["text"]
        await m.edit_text(text)
    else:
        await message.reply_text("please reply to image for ocr")


@pbot.on_message(filters.command(["wasted"]))
async def wasted(bot, message):
    gta = await bot.send_message(message.chat.id, "`Processing...`")
    if not message.reply_to_message:
        await gta.edit("`Reply to a photo :(`")
        return
    ok = message.reply_to_message
    pic = await bot.download_media(ok)
    poto_url = upload_file(pic)
    imglink = f"https://telegra.ph{poto_url[0]}"
    url = f"https://some-random-api.com/canvas/wasted?avatar={imglink}"
    await message.reply_photo(url)
    await gta.delete()
    os.remove(pic)


@pbot.on_message(filters.command(["passed"]))
async def mission_passed(bot, message):
    gta = await bot.send_message(message.chat.id, "`Processing...`")
    if not message.reply_to_message:
        await gta.edit("`Reply to a photo :(`")
        return
    ok = message.reply_to_message
    pic = await bot.download_media(ok)
    poto_url = upload_file(pic)
    imglink = f"https://telegra.ph{poto_url[0]}"
    url = f"https://some-random-api.com/canvas/overlay/passed?avatar={imglink}"
    await message.reply_photo(url)
    await gta.delete()
    os.remove(pic)


async def edit_or_reply(msg: Message, **kwargs):
    func = (
        (msg.edit_text if msg.from_user.is_self else msg.reply)
        if msg.from_user
        else msg.reply
    )
    spec = getfullargspec(func.__wrapped__).args
    return await func(**{k: v for k, v in kwargs.items() if k in spec})


@pbot.on_message(filters.command("tiny"))
async def tiny(client: pbot, message: Message):
    reply = message.reply_to_message
    if not (reply and (reply.media)):
        return await edit_or_reply(message, text="**Please Reply to Sticker**")
    Man = await edit_or_reply(message, text="`Processing . . .`")
    ik = await client.download_media(reply)
    im1 = Image.open("MerissaRobot/Utils/Resources/ken.png")
    if ik.endswith(".tgs"):
        await client.download_media(reply, "man.tgs")
        await bash("lottie_convert.py man.tgs json.json")
        json = open("json.json", "r")
        jsn = json.read()
        jsn = jsn.replace("512", "2000")
        ("json.json", "w").write(jsn)
        await bash("lottie_convert.py json.json man.tgs")
        file = "man.tgs"
        os.remove("json.json")
    elif ik.endswith((".gif", ".mp4")):
        iik = cv2.VideoCapture(ik)
        busy = iik.read()
        cv2.imwrite("i.png", busy)
        fil = "i.png"
        im = Image.open(fil)
        z, d = im.size
        if z == d:
            xxx, yyy = 200, 200
        else:
            t = z + d
            a = z / t
            b = d / t
            aa = (a * 100) - 50
            bb = (b * 100) - 50
            xxx = 200 + 5 * aa
            yyy = 200 + 5 * bb
        k = im.resize((int(xxx), int(yyy)))
        k.save("k.png", format="PNG", optimize=True)
        im2 = Image.open("k.png")
        back_im = im1.copy()
        back_im.paste(im2, (150, 0))
        back_im.save("o.webp", "WEBP", quality=95)
        file = "o.webp"
        os.remove(fil)
        os.remove("k.png")
    else:
        im = Image.open(ik)
        z, d = im.size
        if z == d:
            xxx, yyy = 200, 200
        else:
            t = z + d
            a = z / t
            b = d / t
            aa = (a * 100) - 50
            bb = (b * 100) - 50
            xxx = 200 + 5 * aa
            yyy = 200 + 5 * bb
        k = im.resize((int(xxx), int(yyy)))
        k.save("k.png", format="PNG", optimize=True)
        im2 = Image.open("k.png")
        back_im = im1.copy()
        back_im.paste(im2, (150, 0))
        back_im.save("o.webp", "WEBP", quality=95)
        file = "o.webp"
        os.remove("k.png")
    await message.reply_sticker(file)
    await Man.delete()
    os.remove(file)
    os.remove(ik)


@pbot.on_message(filters.command(["mmf", "memify"]))
async def memify(client: pbot, message: Message):
    if not message.reply_to_message.id:
        await edit_or_reply(message, text="**Please Reply to message!**")
        return
    reply_message = message.reply_to_message
    if not reply_message.media:
        await edit_or_reply(message, text="**Please Reply to Media/Sticker!**")
        return
    file = await client.download_media(reply_message)
    Man = await edit_or_reply(message, text="`Processing . . .`")
    text = message.text.split(None, 1)[1]
    if len(text) < 1:
        return await msg.edit(f"try: `/mmf text`")
    meme = await drawText(file, text)
    await message.reply_sticker(meme)
    await Man.delete()
    os.remove(meme)


async def drawText(image_path, text):
    img = Image.open(image_path)
    os.remove(image_path)
    i_width, i_height = img.size
    if os.name == "nt":
        fnt = "ariel.ttf"
    else:
        fnt = "./MerissaRobot/Utils/Resources/font/default.ttf"
    m_font = ImageFont.truetype(fnt, int((70 / 640) * i_width))
    if ";" in text:
        upper_text, lower_text = text.split(";")
    else:
        upper_text = text
        lower_text = ""
    draw = ImageDraw.Draw(img)
    current_h, pad = 10, 5
    if upper_text:
        for u_text in textwrap.wrap(upper_text, width=15):
            u_width, u_height = draw.textsize(u_text, font=m_font)
            draw.text(
                xy=(((i_width - u_width) / 2) - 2, int((current_h / 640) * i_width)),
                text=u_text,
                font=m_font,
                fill=(0, 0, 0),
            )
            draw.text(
                xy=(((i_width - u_width) / 2) + 2, int((current_h / 640) * i_width)),
                text=u_text,
                font=m_font,
                fill=(0, 0, 0),
            )
            draw.text(
                xy=((i_width - u_width) / 2, int(((current_h / 640) * i_width)) - 2),
                text=u_text,
                font=m_font,
                fill=(0, 0, 0),
            )
            draw.text(
                xy=(((i_width - u_width) / 2), int(((current_h / 640) * i_width)) + 2),
                text=u_text,
                font=m_font,
                fill=(0, 0, 0),
            )

            draw.text(
                xy=((i_width - u_width) / 2, int((current_h / 640) * i_width)),
                text=u_text,
                font=m_font,
                fill=(255, 255, 255),
            )
            current_h += u_height + pad
    if lower_text:
        for l_text in textwrap.wrap(lower_text, width=15):
            u_width, u_height = draw.textsize(l_text, font=m_font)
            draw.text(
                xy=(
                    ((i_width - u_width) / 2) - 2,
                    i_height - u_height - int((20 / 640) * i_width),
                ),
                text=l_text,
                font=m_font,
                fill=(0, 0, 0),
            )
            draw.text(
                xy=(
                    ((i_width - u_width) / 2) + 2,
                    i_height - u_height - int((20 / 640) * i_width),
                ),
                text=l_text,
                font=m_font,
                fill=(0, 0, 0),
            )
            draw.text(
                xy=(
                    (i_width - u_width) / 2,
                    (i_height - u_height - int((20 / 640) * i_width)) - 2,
                ),
                text=l_text,
                font=m_font,
                fill=(0, 0, 0),
            )
            draw.text(
                xy=(
                    (i_width - u_width) / 2,
                    (i_height - u_height - int((20 / 640) * i_width)) + 2,
                ),
                text=l_text,
                font=m_font,
                fill=(0, 0, 0),
            )

            draw.text(
                xy=(
                    (i_width - u_width) / 2,
                    i_height - u_height - int((20 / 640) * i_width),
                ),
                text=l_text,
                font=m_font,
                fill=(255, 255, 255),
            )
            current_h += u_height + pad
    image_name = "memify.webp"
    webp_file = os.path.join(image_name)
    img.save(webp_file, "webp")
    return webp_file
