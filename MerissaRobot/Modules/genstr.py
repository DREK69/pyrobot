from asyncio.exceptions import TimeoutError

from pyrogram import filters, Client
from pyrogram.errors import (
    ApiIdInvalid,
    PasswordHashInvalid,
    PhoneCodeExpired,
    PhoneCodeInvalid,
    PhoneNumberInvalid,
    SessionPasswordNeeded,
)
from pyrogram.types import *
from telethon import TelegramClient
from telethon.errors import (
    ApiIdInvalidError,
    PasswordHashInvalidError,
    PhoneCodeExpiredError,
    PhoneCodeInvalidError,
    PhoneNumberInvalidError,
    SessionPasswordNeededError,
)
from telethon.sessions import StringSession

from MerissaRobot import pbot

ERROR_MESSAGE = (
    "Oops! An exception occurred! \n\n**Error** : {} "
    "\n\nPlease visit @MerissaxSupport if this message doesn't contain any "
    "sensitive information and you if want to report this as "
    "this error message is not being logged by us!"
)

generate_button = [[InlineKeyboardButton("Generate Session", callback_data="generate")]]

# Callbacks
@pbot.on_message(filters.command("genstr"))
async def _callbacks(pbot, message):
    await message.reply_text(
        """Welcome to Merissa Pyrogram and Telethon String Session Generator.

You can procees with bot's api values if you want , else you can proceed with your api values

Bot has over 100+ API ID and HASH Saved , You can use them. 

Press Button Below to Start Generating Session!""",
        reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("Pyrogram", callback_data="gen_pyrogram"),
                            InlineKeyboardButton("Telethon", callback_data="gen_telethon"),
                        ]
                    ]
                ),
            )
    
@pbot.on_callback_query(filters.regex("^gen"))
async def pyro_callbacks(pbot, callback_query):
    query = callback_query.data.split("_")[1]
    await callback_query.answer()
    try:
        if query == "pyrogram":
            await generate_session(pbot, callback_query)
        else:
            await generate_session(pbot, callback_query, telethon=True)
    except Exception as e:
        await callback_query.message.reply(ERROR_MESSAGE.format(str(e)))

async def generate_session(pbot, callback_query, telethon=False):
    msg = callback_query.message
    await msg.reply(
        "Starting {} Session Generation...".format(
            "Telethon" if telethon else "Pyrogram"
        )
    )
    user_id = msg.chat.id
    api_id_msg = await pbot.ask(
        user_id, "Please send your `API_ID` or /skip this Step", filters=filters.text
    )
    if api_id_msg.text == "/skip":
        api_id = "6415310"
        api_hash = "60fe28e5adddbd456871ceeb1cad07e7"
    else:
        try:
            api_id = int(api_id_msg.text)
        except ValueError:
            await api_id_msg.reply(
                "Not a valid API_ID (which must be an integer). Please start generating session again.",
                quote=True,
                reply_markup=InlineKeyboardMarkup(generate_button),
            )
            return
        api_hash_msg = await pbot.ask(
            user_id, "Please send your `API_HASH`", filters=filters.text
        )
        if await cancelled(api_id_msg):
            return
        api_hash = api_hash_msg.text
    phone_number_msg = await pbot.ask(
        user_id,
        "Now please send your `PHONE_NUMBER` along with the country code. \nExample : `+19876543210`",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("Share Contact", request_contact=True)]],
            resize_keyboard=True,
            one_time_keyboard=True)
    )
    while True:
        response: Message = await callback_query.from_user.listen(timeout=60)
        if response.contact:
            phone_number = response.contact.phone_number
            break
        elif response.text == "/cancel":
            await callback_query.message.reply(
                "Current process was canceled.", reply_markup=ReplyKeyboardRemove()
            )
            return
        await response.reply("invalid message type. Please try again.", quote=True)
    await msg.reply("Sending OTP...", reply_markup=ReplyKeyboardRemove())
    if telethon:
        client = TelegramClient(StringSession(), api_id, api_hash)
    else:
        client = Client(":memory:", api_id, api_hash)
    await client.connect()
    try:
        if telethon:
            code = await client.send_code_request(phone_number)
        else:
            code = await client.send_code(phone_number)
    except (ApiIdInvalid, ApiIdInvalidError):
        await msg.reply(
            "`API_ID` and `API_HASH` combination is invalid. Please start generating session again.",
            reply_markup=InlineKeyboardMarkup(generate_button),
        )
        return
    except (PhoneNumberInvalid, PhoneNumberInvalidError):
        await msg.reply(
            "`PHONE_NUMBER` is invalid. Please start generating session again.",
            reply_markup=InlineKeyboardMarkup(generate_button),
        )
        return
    try:
        phone_code_msg = await pbot.ask(
            user_id,
            "Please check for an OTP in official telegram account. If you got it, send OTP here after reading the below format. \nIf OTP is `12345`, **please send it as** `1 2 3 4 5`.",
            filters=filters.text,
            timeout=600,
        )
        if await cancelled(api_id_msg):
            return
    except TimeoutError:
        await msg.reply(
            "Time limit reached of 10 minutes. Please start generating session again.",
            reply_markup=InlineKeyboardMarkup(Data.generate_button),
        )
        return
    phone_code = phone_code_msg.text.replace(" ", "")
    try:
        if telethon:
            await client.sign_in(phone_number, phone_code, password=None)
        else:
            await client.sign_in(phone_number, code.phone_code_hash, phone_code)
    except (PhoneCodeInvalid, PhoneCodeInvalidError):
        await msg.reply(
            "OTP is invalid. Please start generating session again.",
            reply_markup=InlineKeyboardMarkup(generate_button),
        )
        return
    except (PhoneCodeExpired, PhoneCodeExpiredError):
        await msg.reply(
            "OTP is expired. Please start generating session again.",
            reply_markup=InlineKeyboardMarkup(generate_button),
        )
        return
    except (SessionPasswordNeeded, SessionPasswordNeededError):
        try:
            two_step_msg = await pbot.ask(
                user_id,
                "Your account has enabled two-step verification. Please provide the password.",
                filters=filters.text,
                timeout=300,
            )
        except TimeoutError:
            await msg.reply(
                "Time limit reached of 5 minutes. Please start generating session again.",
                reply_markup=InlineKeyboardMarkup(generate_button),
            )
            return
        try:
            password = two_step_msg.text
            if telethon:
                await client.sign_in(password=password)
            else:
                await client.check_password(password=password)
            if await cancelled(api_id_msg):
                return
        except (PasswordHashInvalid, PasswordHashInvalidError):
            await two_step_msg.reply(
                "Invalid Password Provided. Please start generating session again.",
                quote=True,
                reply_markup=InlineKeyboardMarkup(generate_button),
            )
            return
    if telethon:
        string_session = client.session.save()
    else:
        string_session = await client.export_session_string()
    text = "**{} STRING SESSION** \n\n`{}` \n\nGenerated by @MerissaRobot".format(
        "TELETHON" if telethon else "PYROGRAM", string_session
    )
    await client.send_message("me", text)
    await client.disconnect()
    await phone_code_msg.reply(
        "Successfully generated {} string session. \n\nPlease check your saved messages! \n\nBy @MerissaRobot".format(
            "telethon" if telethon else "pyrogram"
        )
    )

async def cancelled(msg):
    if "/cancel" in msg.text:
        await msg.reply(
            "Cancelled the Process!",
            quote=True,
            reply_markup=InlineKeyboardMarkup(generate_button),
        )
        return True
    elif "/restart" in msg.text:
        await msg.reply(
            "Restarted the Bot!",
            quote=True,
            reply_markup=InlineKeyboardMarkup(generate_button),
        )
        return True
    else:
        return False
