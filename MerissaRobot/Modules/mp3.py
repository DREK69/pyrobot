import os

from pyrogram import filters
from moviepy.editor import VideoFileClip

from MerissaRobot import pbot

@pbot.on_message(filters.command("audio") & filters.private)
async def videotoaudio(client, message):
    reply = message.reply_to_message
    m = await message.reply_text("Creating your video to audio... Please wait!")
    if reply:
        if reply.video:
            download_location = await client.download_media(
                message=reply,
                file_name="root/downloads/",
            )
            video = VideoFileClip(download_location)
            audio = video.audio
            audio.write_audiofile("merissa-audio.m4a")
            audio.close()
            video.close()
            audio2 = open('merissa-audio.m4a', 'rb')
            await message.reply_audio(audio2)
            os.remove(audio2)
    else:
        return await m.edit_text("Please Reply to Video for convert mp3 audio")
