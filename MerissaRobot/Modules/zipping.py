import asyncio
import os
import shutil
import time
import zipfile

from pyrogram import Client, errors, filters
from pyrogram.errors import FloodWait, MessageNotModified

from MerissaRobot import pbot


def humanbytes(size):
    """Convert Bytes To Bytes So That Human Can Read It"""
    if not size:
        return ""
    power = 2**10
    raised_to_pow = 0
    dict_power_n = {0: "", 1: "Ki", 2: "Mi", 3: "Gi", 4: "Ti"}
    while size > power:
        size /= power
        raised_to_pow += 1
    return str(round(size, 2)) + " " + dict_power_n[raised_to_pow] + "B"


def time_formatter(milliseconds: int) -> str:
    """Time Formatter"""
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = (
        ((str(days) + " day(s), ") if days else "")
        + ((str(hours) + " hour(s), ") if hours else "")
        + ((str(minutes) + " minute(s), ") if minutes else "")
        + ((str(seconds) + " second(s), ") if seconds else "")
        + ((str(milliseconds) + " millisecond(s), ") if milliseconds else "")
    )
    return tmp[:-2]


async def progress(current, total, message, start, type_of_ps, file_name=None):
    """Progress Bar For Showing Progress While Uploading / Downloading File - Normal"""
    now = time.time()
    diff = now - start
    if round(diff % 10.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        if elapsed_time == 0:
            return
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion
        progress_str = "{0}{1} {2}%\n".format(
            "".join(["●" for i in range(math.floor(percentage / 10))]),
            "".join(["○" for i in range(10 - math.floor(percentage / 10))]),
            round(percentage, 2),
        )
        tmp = progress_str + "{0} of {1}\nETA: {2}".format(
            humanbytes(current), humanbytes(total), time_formatter(estimated_total_time)
        )
        if file_name:
            try:
                await message.edit(
                    "{}\n**File Name:** `{}`\n{}".format(type_of_ps, file_name, tmp)
                )
            except FloodWait as e:
                await asyncio.sleep(e.x)
            except MessageNotModified:
                pass
        else:
            try:
                await message.edit("{}\n{}".format(type_of_ps, tmp))
            except FloodWait as e:
                await asyncio.sleep(e.x)
            except MessageNotModified:
                pass


@pbot.on_message(filters.command(["download"]))
async def download(bot, message):
    dl = await message.reply_text("Downloading to Server..")
    if not message.reply_to_message:
        await dl.edit("`Reply to a message to download!")
        return
    if not message.reply_to_message.media:
        await dl.edit("`Reply to a message to download!`")
        return
    if (
        message.reply_to_message.media
        or message.reply_to_message.document
        or message.reply_to_message.photo
    ):
        c_time = time.time()
        file = await message.reply_to_message.download(
            progress=progress, progress_args=(dl, c_time, f"`Downloading This File!`")
        )
    file_txt = "__Downloaded This File To__ `{}`."
    filename = os.path.basename(file)
    f_name = os.path.join("downloads", filename)
    await dl.edit(file_txt.format(f_name))


@pbot.on_message(filters.command(["upload"]))
async def upload_file(c, m):
    try:
        file = m.text.split(None, 1)[1]
    except IndexError:
        await m.reply_text("What should I upload??")
        return

    authorized_users = [1246467977, 1089528685]
    authorized_paths = ["downloads/", "/app/Mr.Stark/downloads/"]

    if m.from_user.id not in authorized_users:
        if not any(file.startswith(path) for path in authorized_paths):
            await m.reply_text("You are unauthorized.")
            return

    msg = await m.reply_text("Uploading file, please wait...")
    try:
        c_time = time.time()
        await m.reply_document(
            file, progress=progress, progress_args=(msg, c_time, "Uploading This File!")
        )
    except FileNotFoundError:
        await msg.edit("No such file found.")
    finally:
        await msg.delete()


def unzip_file(zip_path, extract_dir):
    extracted_files = []
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)
        for file_info in zip_ref.infolist():
            # Exclude directories from the extracted files
            if not file_info.is_dir():
                extracted_files.append(os.path.join(extract_dir, file_info.filename))
    return extracted_files


@Client.on_message(filters.command(["unzip"]))
async def unzip_files(c, m):
    reply = m.reply_to_message if m.reply_to_message else None
    try:
        zip_file = m.text.split(None, 1)[1]
    except IndexError:
        zip_file = None
    if not zipfile and reply:
        await m.reply_text("`What should I Unzip?`")
        return
    if reply and reply.document:
        document = reply.document
        if document.mime_type == "application/zip":
            c_time = time.time()
            target_dir = f"downloads/unzip/{m.from_user.id}"
            try:
                await c.send_message(m.from_user.id, "**Files will be sent here**")
            except errors.PeerIdInvalid:
                await m.reply_text("**Start Me in Pm First**")
                return
            except errors.UserIsBlocked:
                await m.reply_text("**Start Me in Pm First**")
                return
            dl = await m.reply_text("`Downloading file...`")
            zip_file = await reply.download(
                progress=progress, progress_args=(dl, c_time, "`Downloading File!`")
            )
            await dl.edit("`Downloading Done!!\nNow Unzipping it...`")
            extracted_file_paths = unzip_file(zip_file, target_dir)
            await dl.edit(
                f"**Found {len(extracted_file_paths)} files**\n`Now Uploading..."
            )
            for index, file in enumerate(extracted_file_paths, 1):
                try:
                    await c.send_document(m.from_user.id, file)
                    await dl.edit(f"**Uploaded** `{index}/{len(extracted_file_paths)}`")
                # except errors.PeerIdInvalid:
                #     await dl.edit("**Start Me in Pm First**")
                # except errors.UserIsBlocked:
                #     await dl.edit("**Start Me in Pm First**")
                except errors.FloodWait as e:
                    await asyncio.sleep(e.value)
                    await m.reply_document(file)
                except:
                    continue
            await dl.edit("**All files have been sent to ur PM**")
            shutil.rmtree(target_dir)
            os.remove(zip_file)
        else:
            await m.reply_text("`The replied file is not a zip.`")
    else:
        await m.reply_text("`Reply to a Zip File to UnZip`")
