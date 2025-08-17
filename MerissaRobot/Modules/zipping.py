import asyncio
import os
import shutil
import time
import zipfile
import math

from pyrogram import Client, errors, filters
from pyrogram.errors import FloodWait, MessageNotModified

from MerissaRobot import pbot


# -------- Utils -------- #

def humanbytes(size: int) -> str:
    """Convert bytes to human readable format"""
    if not size:
        return ""
    power = 2**10
    n = 0
    units = ["", "Ki", "Mi", "Gi", "Ti"]
    while size >= power and n < len(units) - 1:
        size /= power
        n += 1
    return f"{round(size, 2)} {units[n]}B"


def time_formatter(milliseconds: int) -> str:
    """Format time in milliseconds to human readable"""
    seconds, ms = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    result = (
        (f"{days}d, " if days else "")
        + (f"{hours}h, " if hours else "")
        + (f"{minutes}m, " if minutes else "")
        + (f"{seconds}s, " if seconds else "")
        + (f"{ms}ms, " if ms else "")
    )
    return result.strip(", ")


async def progress(current, total, message, start, status, file_name=None):
    """Progress bar for uploads/downloads"""
    now = time.time()
    diff = now - start
    if current == total or diff % 5 == 0:  # update every 5 sec
        percent = current * 100 / total
        speed = current / diff if diff > 0 else 0
        elapsed_time = round(diff) * 1000
        remaining = round((total - current) / speed) * 1000 if speed != 0 else 0
        eta = time_formatter(elapsed_time + remaining)

        bar = "●" * math.floor(percent / 10) + "○" * (10 - math.floor(percent / 10))
        text = f"{status}\n\n[{bar}] {round(percent, 2)}%\n\n" \
               f"📂 {humanbytes(current)} of {humanbytes(total)}\n" \
               f"⚡ Speed: {humanbytes(speed)}/s\n" \
               f"⏳ ETA: {eta}"

        if file_name:
            text = f"**File:** `{file_name}`\n\n" + text

        try:
            await message.edit(text)
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except MessageNotModified:
            pass


# -------- Download -------- #

@pbot.on_message(filters.command("download"))
async def download(bot, message):
    if not message.reply_to_message or not message.reply_to_message.media:
        return await message.reply_text("⚠️ Reply to a file, video, or photo to download!")

    status = await message.reply_text("📥 Downloading to server...")
    c_time = time.time()
    try:
        file_path = await message.reply_to_message.download(
            progress=progress,
            progress_args=(status, c_time, "📥 Downloading...")
        )
    except Exception as e:
        return await status.edit(f"❌ Download failed: `{e}`")

    filename = os.path.basename(file_path)
    saved_path = os.path.join("downloads", filename)
    await status.edit(f"✅ **Downloaded Successfully!**\n\n📂 Saved to: `{saved_path}`")


# -------- Upload -------- #

@pbot.on_message(filters.command("upload"))
async def upload_file(c, m):
    try:
        file = m.text.split(None, 1)[1]
    except IndexError:
        return await m.reply_text("⚠️ Usage: `/upload <file path>`")

    authorized_users = [1246467977, 1089528685]
    authorized_paths = ["downloads/", "/app/Mr.Stark/downloads/"]

    if m.from_user.id not in authorized_users and not any(file.startswith(p) for p in authorized_paths):
        return await m.reply_text("❌ You are not authorized to upload from this path.")

    status = await m.reply_text("📤 Uploading file...")
    c_time = time.time()

    try:
        await m.reply_document(
            file,
            progress=progress,
            progress_args=(status, c_time, "📤 Uploading...")
        )
        await status.edit("✅ Upload complete!")
    except FileNotFoundError:
        await status.edit("❌ File not found.")
    except Exception as e:
        await status.edit(f"❌ Upload failed: `{e}`")


# -------- Unzip -------- #

def unzip_file(zip_path, extract_dir):
    extracted_files = []
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)
        for file_info in zip_ref.infolist():
            if not file_info.is_dir():
                extracted_files.append(os.path.join(extract_dir, file_info.filename))
    return extracted_files


@pbot.on_message(filters.command("unzip"))
async def unzip_files(c, m):
    reply = m.reply_to_message
    if not reply or not reply.document:
        return await m.reply_text("⚠️ Reply to a `.zip` file to unzip.")

    if reply.document.mime_type != "application/zip":
        return await m.reply_text("❌ The replied file is not a zip archive.")

    status = await m.reply_text("📥 Downloading zip...")
    c_time = time.time()

    try:
        zip_file = await reply.download(
            progress=progress,
            progress_args=(status, c_time, "📥 Downloading zip...")
        )
    except Exception as e:
        return await status.edit(f"❌ Download failed: `{e}`")

    extract_dir = f"downloads/unzip/{m.from_user.id}"
    os.makedirs(extract_dir, exist_ok=True)

    await status.edit("📂 Extracting zip file...")
    extracted_files = unzip_file(zip_file, extract_dir)

    if not extracted_files:
        return await status.edit("❌ No files extracted.")
    await status.edit(f"✅ Extracted `{len(extracted_files)}` files.\n📤 Uploading...")

    # Upload files privately
    try:
        await c.send_message(m.from_user.id, "📂 **Your extracted files:**")
    except (errors.PeerIdInvalid, errors.UserIsBlocked):
        return await status.edit("⚠️ Please start the bot in PM first.")

    for i, file in enumerate(extracted_files, 1):
        try:
            await c.send_document(m.from_user.id, file)
            await status.edit(f"📤 Uploaded `{i}/{len(extracted_files)}` files...")
            await asyncio.sleep(0.5)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await c.send_document(m.from_user.id, file)
        except Exception:
            continue

    await status.edit("✅ All files have been uploaded to your PM.")
    shutil.rmtree(extract_dir, ignore_errors=True)
    os.remove(zip_file)
