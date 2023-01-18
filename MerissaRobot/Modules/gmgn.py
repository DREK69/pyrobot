import time

from telegram import ParseMode
from telegram.ext import Filters, MessageHandler

from MerissaRobot import dispatcher

MEDIA_GM = "https://telegra.ph/file/fff37608fa21d9d3d0b39.jpg"
MEDIA_GN = "https://telegra.ph/file/1862c7260109e24ed4715.jpg"
MEDIA_HELLO = "https://telegra.ph/file/f3f2dc386a33e37f6cb05.png"
MEDIA_BYE = "https://telegra.ph/file/061054c8f73fe7ffbf6aa.mp4"

IMG_GM = MEDIA_GM.split(".")
gm_id = IMG_GM[-1]

IMG_GN = MEDIA_GM.split(".")
gn_id = IMG_GN[-1]

IMG_HELLO = MEDIA_HELLO.split(".")
hello_id = IMG_HELLO[-1]

IMG_BYE = MEDIA_BYE.split(".")
bye_id = IMG_BYE[-1]


def goodnight(update, context):
    message = update.effective_message
    user1 = message.from_user.first_name
    update.effective_chat.id
    try:
        if gn_id in ("jpeg", "jpg", "png"):
            update.effective_message.reply_photo(
                MEDIA_GN,
                caption=f"*Good Night:* {user1}",
                parse_mode=ParseMode.MARKDOWN,
            )
        elif gn_id in ("mp4", "mkv"):
            update.effective_message.reply_video(
                MEDIA_GN,
                caption=f"*Good Night:* {user1}",
                parse_mode=ParseMode.MARKDOWN,
            )
        elif gn_id in ("gif", "webp"):
            update.effective_message.reply_animation(
                MEDIA_GN,
                caption=f"*Good Night:* {user1}",
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            reply = f"*Good Night:* {user1}"
            message.reply_text(reply)

    except:
        reply = f"*Good Night:* {user1}"
        message.reply_text(reply)

    time.sleep(5)


def goodmorning(update, context):
    message = update.effective_message
    user1 = message.from_user.first_name
    update.effective_chat.id
    try:
        if gm_id in ("jpeg", "jpg", "png"):
            update.effective_message.reply_photo(
                MEDIA_GM,
                caption=f"*Good Morning:* {user1}",
                parse_mode=ParseMode.MARKDOWN,
            )
        elif gm_id in ("mp4", "mkv"):
            update.effective_message.reply_video(
                MEDIA_GM,
                caption=f"*Good Morning:* {user1}",
                parse_mode=ParseMode.MARKDOWN,
            )
        elif gm_id in ("gif", "webp"):
            update.effective_message.reply_animation(
                MEDIA_GM,
                caption=f"*Good Morning:* {user1}",
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            reply = f"*Good Morning:* {user1}"
            message.reply_text(reply)
    except:
        reply = f"*Good Morning:* {user1}"
        message.reply_text(reply)

    time.sleep(5)


def hello(update, context):
    message = update.effective_message
    user1 = message.from_user.first_name
    update.effective_chat.id
    try:
        if hello_id in ("jpeg", "jpg", "png"):
            update.effective_message.reply_photo(
                MEDIA_HELLO,
                caption=f"*Hello* {user1}",
                parse_mode=ParseMode.MARKDOWN,
            )
        elif hello_id in ("mp4", "mkv"):
            update.effective_message.reply_video(
                MEDIA_HELLO,
                caption=f"*Hello* {user1}",
                parse_mode=ParseMode.MARKDOWN,
            )
        elif hello_id in ("gif", "webp"):
            update.effective_message.reply_animation(
                MEDIA_HELLO,
                caption=f"*Hello* {user1}",
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            reply = f"*Hello* {user1}"
            message.reply_text(reply)
    except:
        reply = f"*Hello* {user1}"
        message.reply_text(reply)

    time.sleep(5)


def bye(update, context):
    message = update.effective_message
    user1 = message.from_user.first_name
    update.effective_chat.id
    try:
        if bye_id in ("jpeg", "jpg", "png"):
            update.effective_message.reply_photo(
                MEDIA_BYE,
                caption=f"*Bye!!* {user1}",
                parse_mode=ParseMode.MARKDOWN,
            )
        elif bye_id in ("mp4", "mkv"):
            update.effective_message.reply_video(
                MEDIA_BYE,
                caption=f"*Bye!!* {user1}",
                parse_mode=ParseMode.MARKDOWN,
            )
        elif bye_id in ("gif", "webp"):
            update.effective_message.reply_animation(
                MEDIA_BYE,
                caption=f"*Bye!!* {user1}",
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            reply = f"*Bye!!* {user1}"
            message.reply_text(reply)
    except:
        reply = f"*Bye!!* {user1}"
        message.reply_text(reply)

    time.sleep(5)


GDMORNING_HANDLER = MessageHandler(
    Filters.regex("^(?i)(good morning|goodmorning|gm)"),
    goodmorning,
    friendly="goodmorning",
    run_async=True,
)
GDNIGHT_HANDLER = MessageHandler(
    Filters.regex("^(?i)(good night|goodnight|gn)"),
    goodnight,
    friendly="goodnight",
    run_async=True,
)
BYE_HANDLER = MessageHandler(
    Filters.regex("^(?i)(bye)"), bye, friendly="bye", run_async=True
)
HELLO_HANDLER = MessageHandler(
    Filters.regex("^(?i)(hello)"), hello, friendly="hello", run_async=True
)

dispatcher.add_handler(GDMORNING_HANDLER)
dispatcher.add_handler(GDNIGHT_HANDLER)
dispatcher.add_handler(HELLO_HANDLER)
dispatcher.add_handler(BYE_HANDLER)
