from pyrogram import filters

from MerissaRobot import pbot
from MerissaRobot.helpers import getreq as get


@pbot.on_message(filters.command("hug"))
async def animegif(_, message):
    x = await get(f"https://api.princexd.tech/anime/hug")
    await message.reply_video(
        x["url"],
        caption="Powered by @MerissaRobot",
    )


@pbot.on_message(filters.command("cuddle"))
async def animegif(_, message):
    x = await get(f"https://api.princexd.tech/anime/cuddle")
    await message.reply_video(
        x["url"],
        caption="Powered by @MerissaRobot",
    )


@pbot.on_message(filters.command("poke"))
async def animegif(_, message):
    x = await get(f"https://api.princexd.tech/anime/poke")
    await message.reply_video(
        x["url"],
        caption="Powered by @MerissaRobot",
    )


@pbot.on_message(filters.command("facepalm"))
async def animegif(_, message):
    x = await get(f"https://api.princexd.tech/anime/facepalm")
    await message.reply_video(
        x["url"],
        caption="Powered by @MerissaRobot",
    )


@pbot.on_message(filters.command("stare"))
async def animegif(_, message):
    x = await get(f"https://api.princexd.tech/anime/stare")
    await message.reply_video(
        x["url"],
        caption="Powered by @MerissaRobot",
    )


@pbot.on_message(filters.command("pout"))
async def animegif(_, message):
    x = await get(f"https://api.princexd.tech/anime/pout")
    await message.reply_video(
        x["url"],
        caption="Powered by @MerissaRobot",
    )


@pbot.on_message(filters.command("handhold"))
async def animegif(_, message):
    x = await get(f"https://api.princexd.tech/anime/handhold")
    await message.reply_video(
        x["url"],
        caption="Powered by @MerissaRobot",
    )


@pbot.on_message(filters.command("wave"))
async def animegif(_, message):
    x = await get(f"https://api.princexd.tech/anime/wave")
    await message.reply_video(
        x["url"],
        caption="Powered by @MerissaRobot",
    )


@pbot.on_message(filters.command("blush"))
async def animegif(_, message):
    x = await get(f"https://api.princexd.tech/anime/blush")
    await message.reply_video(
        x["url"],
        caption="Powered by @MerissaRobot",
    )


@pbot.on_message(filters.command("dance"))
async def animegif(_, message):
    x = await get(f"https://api.princexd.tech/anime/dance")
    await message.reply_video(
        x["url"],
        caption="Powered by @MerissaRobot",
    )


@pbot.on_message(filters.command("baka"))
async def animegif(_, message):
    x = await get(f"https://api.princexd.tech/anime/baka")
    await message.reply_video(
        x["url"],
        caption="Powered by @MerissaRobot",
    )


@pbot.on_message(filters.command("bore"))
async def animegif(_, message):
    x = await get(f"https://api.princexd.tech/anime/bare")
    await message.reply_video(
        x["url"],
        caption="Powered by @MerissaRobot",
    )


@pbot.on_message(filters.command("laugh"))
async def animegif(_, message):
    x = await get(f"https://api.princexd.tech/anime/laugh")
    await message.reply_video(
        x["url"],
        caption="Powered by @MerissaRobot",
    )


@pbot.on_message(filters.command("smug"))
async def animegif(_, message):
    x = await get(f"https://api.princexd.tech/anime/smug")
    await message.reply_video(
        x["url"],
        caption="Powered by @MerissaRobot",
    )


@pbot.on_message(filters.command("thumbsup"))
async def animegif(_, message):
    x = await get(f"https://api.princexd.tech/anime/thumbsup")
    await message.reply_video(
        x["url"],
        caption="Powered by @MerissaRobot",
    )


@pbot.on_message(filters.command("shoot"))
async def animegif(_, message):
    x = await get(f"https://api.princexd.tech/anime/shoot")
    await message.reply_video(
        x["url"],
        caption="Powered by @MerissaRobot",
    )


@pbot.on_message(filters.command("tickle"))
async def animegif(_, message):
    x = await get(f"https://api.princexd.tech/anime/tickle")
    await message.reply_video(
        x["url"],
        caption="Powered by @MerissaRobot",
    )


@pbot.on_message(filters.command("feed"))
async def animegif(_, message):
    x = await get(f"https://api.princexd.tech/anime/feed")
    await message.reply_video(
        x["url"],
        caption="Powered by @MerissaRobot",
    )


@pbot.on_message(filters.command("think"))
async def animegif(_, message):
    x = await get(f"https://api.princexd.tech/anime/think")
    await message.reply_video(
        x["url"],
        caption="Powered by @MerissaRobot",
    )


@pbot.on_message(filters.command("wink"))
async def animegif(_, message):
    x = await get(f"https://api.princexd.tech/anime/wink")
    await message.reply_video(
        x["url"],
        caption="Powered by @MerissaRobot",
    )


@pbot.on_message(filters.command("sleep"))
async def animegif(_, message):
    x = await get(f"https://api.princexd.tech/anime/sleep")
    await message.reply_video(
        x["url"],
        caption="Powered by @MerissaRobot",
    )


@pbot.on_message(filters.command("punch"))
async def animegif(_, message):
    x = await get(f"https://api.princexd.tech/anime/punch")
    await message.reply_video(
        x["url"],
        caption="Powered by @MerissaRobot",
    )


@pbot.on_message(filters.command("cry"))
async def animegif(_, message):
    x = await get(f"https://api.princexd.tech/anime/cry")
    await message.reply_video(
        x["url"],
        caption="Powered by @MerissaRobot",
    )


@pbot.on_message(filters.command("kill"))
async def animegif(_, message):
    x = await get(f"https://api.princexd.tech/anime/kill")
    await message.reply_video(
        x["url"],
        caption="Powered by @MerissaRobot",
    )


@pbot.on_message(filters.command("smile"))
async def animegif(_, message):
    x = await get(f"https://api.princexd.tech/anime/smile")
    await message.reply_video(
        x["url"],
        caption="Powered by @MerissaRobot",
    )


@pbot.on_message(filters.command("highfive"))
async def animegif(_, message):
    x = await get(f"https://api.princexd.tech/anime/highfive")
    await message.reply_video(
        x["url"],
        caption="Powered by @MerissaRobot",
    )


@pbot.on_message(filters.command("slap"))
async def animegif(_, message):
    x = await get(f"https://api.princexd.tech/anime/slap")
    await message.reply_video(
        x["url"],
        caption="Powered by @MerissaRobot",
    )


@pbot.on_message(filters.command("pat"))
async def animegif(_, message):
    x = await get(f"https://api.princexd.tech/anime/pat")
    await message.reply_video(
        x["url"],
        caption="Powered by @MerissaRobot",
    )
