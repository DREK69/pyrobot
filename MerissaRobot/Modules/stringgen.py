import traceback
from asyncio.exceptions import TimeoutError

from pyrogram import Client, filters
from MerissaRobot import pbot as Client 
from pyrogram1 import Client as Client1
from pyrogram1.errors import ApiIdInvalid as ApiIdInvalid1
from pyrogram1.errors import PasswordHashInvalid as PasswordHashInvalid1
from pyrogram1.errors import PhoneCodeExpired as PhoneCodeExpired1
from pyrogram1.errors import PhoneCodeInvalid as PhoneCodeInvalid1
from pyrogram1.errors import PhoneNumberInvalid as PhoneNumberInvalid1
from pyrogram1.errors import SessionPasswordNeeded as SessionPasswordNeeded1
from pyrogram.errors import (
    ApiIdInvalid,
    PasswordHashInvalid,
    PhoneCodeExpired,
    PhoneCodeInvalid,
    PhoneNumberInvalid,
    SessionPasswordNeeded,
)
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from pyromod import listen  # ignore
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


# Callbacks
@Client.on_callback_query()
async def _callbacks(bot: Client, callback_query: CallbackQuery):
    user = await bot.get_me()
    # user_id = callback_query.from_user.id
    mention = user.mention
    query = callback_query.data.lower()
    if query.startswith("home"):
        if query == "home":
            chat_id = callback_query.from_user.id
            message_id = callback_query.message.id
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=Data.START.format(callback_query.from_user.mention, mention),
                reply_markup=InlineKeyboardMarkup(Data.buttons),
            )
    elif query == "about":
        chat_id = callback_query.from_user.id
        message_id = callback_query.message.id
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=Data.ABOUT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(Data.home_buttons),
        )
    elif query == "help":
        chat_id = callback_query.from_user.id
        message_id = callback_query.message.id
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=Data.HELP,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(Data.home_buttons),
        )
    elif query == "generate":
        await callback_query.answer()
        await callback_query.message.reply(
            ask_ques, reply_markup=InlineKeyboardMarkup(buttons_ques)
        )
    elif query.startswith("pyrogram") or query.startswith("telethon"):
        try:
            if query == "pyrogram":
                await callback_query.answer(
                    "Please note that the new type of string sessions may not work in all bots, i.e, only the bots that have been updated to pyrogram v2 will work!",
                    show_alert=True,
                )
                await generate_session(bot, callback_query.message)
            elif query == "pyrogram1":
                await callback_query.answer()
                await generate_session(bot, callback_query.message, old_pyro=True)
            elif query == "pyrogram_bot":
                await callback_query.answer(
                    "Please note that this bot session will be of pyrogram v2",
                    show_alert=True,
                )
                await generate_session(bot, callback_query.message, is_bot=True)
            elif query == "telethon_bot":
                await callback_query.answer()
                await generate_session(
                    bot, callback_query.message, telethon=True, is_bot=True
                )
            elif query == "telethon":
                await callback_query.answer()
                await generate_session(bot, callback_query.message, telethon=True)
        except Exception as e:
            print(traceback.format_exc())
            print(e)
            await callback_query.message.reply(ERROR_MESSAGE.format(str(e)))


ERROR_MESSAGE = (
    "Oops! An exception occurred! \n\n**Error** : {} "
    "\n\nPlease visit @StarkBotsChat if this message doesn't contain any "
    "sensitive information and you if want to report this as "
    "this error message is not being logged by us!"
)


class Data:
    generate_single_button = [
        InlineKeyboardButton("🔥 Start Generating Session 🔥", callback_data="generate")
    ]

    home_buttons = [
        generate_single_button,
        [InlineKeyboardButton(text="🏠 Return Home 🏠", callback_data="home")],
    ]

    generate_button = [generate_single_button]

    buttons = [
        generate_single_button,
        [
            InlineKeyboardButton(
                "✨ Bot Status and More Bots ✨", url="https://t.me/StarkBots/7"
            )
        ],
        [
            InlineKeyboardButton("How to Use ❔", callback_data="help"),
            InlineKeyboardButton("🎪 About 🎪", callback_data="about"),
        ],
        [InlineKeyboardButton("♥ More Amazing bots ♥", url="https://t.me/StarkBots")],
    ]

    START = """
Hey {}

Welcome to {}

If you don't trust this bot, 
1) stop reading this message
2) delete this chat

Still reading?
You can use me to generate pyrogram (even version 2) and telethon string session. Use below buttons to learn more !

By @StarkBots
    """

    HELP = """
✨ **Available Commands** ✨

/about - About The Bot
/help - This Message
/start - Start the Bot
/generate - Generate Session
/cancel - Cancel the process
/restart - Cancel the process
"""

    ABOUT = """
**About This Bot** 

Telegram Bot to generate Pyrogram and Telethon string session by @StarkBots

Source Code : [Click Here](https://github.com/StarkBotsIndustries/StringSessionBot)

Framework : [Pyrogram](https://docs.pyrogram.org)

Language : [Python](https://www.python.org)

Developer : @StarkProgrammer
    """


ask_ques = "Please choose the python library you want to generate string session for"
buttons_ques = [
    [
        InlineKeyboardButton("Pyrogram", callback_data="pyrogram1"),
        InlineKeyboardButton("Telethon", callback_data="telethon"),
    ],
    [
        InlineKeyboardButton("Pyrogram v2 [New]", callback_data="pyrogram"),
    ],
    [
        InlineKeyboardButton("Pyrogram Bot", callback_data="pyrogram_bot"),
        InlineKeyboardButton("Telethon Bot", callback_data="telethon_bot"),
    ],
]


@Client.on_message(filters.private & ~filters.forwarded & filters.command("generate"))
async def main(_, msg):
    await msg.reply(ask_ques, reply_markup=InlineKeyboardMarkup(buttons_ques))


async def generate_session(
    bot: Client,
    msg: Message,
    telethon=False,
    old_pyro: bool = False,
    is_bot: bool = False,
):
    if telethon:
        ty = "Telethon"
    else:
        ty = "Pyrogram"
        if not old_pyro:
            ty += " v2"
    if is_bot:
        ty += " Bot"
    await msg.reply(f"Starting {ty} Session Generation...")
    user_id = msg.chat.id
    api_id_msg = await bot.ask(
        user_id, "Please send your `API_ID`", filters=filters.text
    )
    if await cancelled(api_id_msg):
        return
    try:
        api_id = int(api_id_msg.text)
    except ValueError:
        await api_id_msg.reply(
            "Not a valid API_ID (which must be an integer). Please start generating session again.",
            quote=True,
            reply_markup=InlineKeyboardMarkup(Data.generate_button),
        )
        return
    api_hash_msg = await bot.ask(
        user_id, "Please send your `API_HASH`", filters=filters.text
    )
    if await cancelled(api_hash_msg):
        return
    api_hash = api_hash_msg.text
    if not is_bot:
        t = "Now please send your `PHONE_NUMBER` along with the country code. \nExample : `+19876543210`'"
    else:
        t = "Now please send your `BOT_TOKEN` \nExample : `12345:abcdefghijklmnopqrstuvwxyz`'"
    phone_number_msg = await bot.ask(user_id, t, filters=filters.text)
    if await cancelled(phone_number_msg):
        return
    phone_number = phone_number_msg.text
    if not is_bot:
        await msg.reply("Sending OTP...")
    else:
        await msg.reply("Logging as Bot User...")
    if telethon and is_bot:
        client = TelegramClient(StringSession(), api_id, api_hash)
    elif telethon:
        client = TelegramClient(StringSession(), api_id, api_hash)
    elif is_bot:
        client = Client(
            name="bot",
            api_id=api_id,
            api_hash=api_hash,
            bot_token=phone_number,
            in_memory=True,
        )
    elif old_pyro:
        client = Client1(":memory:", api_id=api_id, api_hash=api_hash)
    else:
        client = Client(name="user", api_id=api_id, api_hash=api_hash, in_memory=True)
    await client.connect()
    try:
        code = None
        if not is_bot:
            if telethon:
                code = await client.send_code_request(phone_number)
            else:
                code = await client.send_code(phone_number)
    except (ApiIdInvalid, ApiIdInvalidError, ApiIdInvalid1):
        await msg.reply(
            "`API_ID` and `API_HASH` combination is invalid. Please start generating session again.",
            reply_markup=InlineKeyboardMarkup(Data.generate_button),
        )
        return
    except (PhoneNumberInvalid, PhoneNumberInvalidError, PhoneNumberInvalid1):
        await msg.reply(
            "`PHONE_NUMBER` is invalid. Please start generating session again.",
            reply_markup=InlineKeyboardMarkup(Data.generate_button),
        )
        return
    try:
        phone_code_msg = None
        if not is_bot:
            phone_code_msg = await bot.ask(
                user_id,
                "Please check for an OTP in official telegram account. If you got it, send OTP here after reading the below format. \nIf OTP is `12345`, **please send it as** `1 2 3 4 5`.",
                filters=filters.text,
                timeout=600,
            )
            if await cancelled(phone_code_msg):
                return
    except TimeoutError:
        await msg.reply(
            "Time limit reached of 10 minutes. Please start generating session again.",
            reply_markup=InlineKeyboardMarkup(Data.generate_button),
        )
        return
    if not is_bot:
        phone_code = phone_code_msg.text.replace(" ", "")
        try:
            if telethon:
                await client.sign_in(phone_number, phone_code, password=None)
            else:
                await client.sign_in(phone_number, code.phone_code_hash, phone_code)
        except (PhoneCodeInvalid, PhoneCodeInvalidError, PhoneCodeInvalid1):
            await msg.reply(
                "OTP is invalid. Please start generating session again.",
                reply_markup=InlineKeyboardMarkup(Data.generate_button),
            )
            return
        except (PhoneCodeExpired, PhoneCodeExpiredError, PhoneCodeExpired1):
            await msg.reply(
                "OTP is expired. Please start generating session again.",
                reply_markup=InlineKeyboardMarkup(Data.generate_button),
            )
            return
        except (
            SessionPasswordNeeded,
            SessionPasswordNeededError,
            SessionPasswordNeeded1,
        ):
            try:
                two_step_msg = await bot.ask(
                    user_id,
                    "Your account has enabled two-step verification. Please provide the password.",
                    filters=filters.text,
                    timeout=300,
                )
            except TimeoutError:
                await msg.reply(
                    "Time limit reached of 5 minutes. Please start generating session again.",
                    reply_markup=InlineKeyboardMarkup(Data.generate_button),
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
            except (
                PasswordHashInvalid,
                PasswordHashInvalidError,
                PasswordHashInvalid1,
            ):
                await two_step_msg.reply(
                    "Invalid Password Provided. Please start generating session again.",
                    quote=True,
                    reply_markup=InlineKeyboardMarkup(Data.generate_button),
                )
                return
    else:
        if telethon:
            await client.start(bot_token=phone_number)
        else:
            await client.sign_in_bot(phone_number)
    if telethon:
        string_session = client.session.save()
    else:
        string_session = await client.export_session_string()
    text = f"**{ty.upper()} STRING SESSION** \n\n`{string_session}` \n\nGenerated by @StarkStringGenBot"
    try:
        if not is_bot:
            await client.send_message("me", text)
        else:
            await bot.send_message(msg.chat.id, text)
    except KeyError:
        pass
    await client.disconnect()
    await bot.send_message(
        msg.chat.id,
        "Successfully generated {} string session. \n\nPlease check your saved messages! \n\nBy @StarkBots".format(
            "telethon" if telethon else "pyrogram"
        ),
    )


async def cancelled(msg):
    if "/cancel" in msg.text:
        await msg.reply(
            "Cancelled the Process!",
            quote=True,
            reply_markup=InlineKeyboardMarkup(Data.generate_button),
        )
        return True
    elif "/restart" in msg.text:
        await msg.reply(
            "Restarted the Bot!",
            quote=True,
            reply_markup=InlineKeyboardMarkup(Data.generate_button),
        )
        return True
    elif msg.text.startswith("/"):  # Bot Commands
        await msg.reply("Cancelled the generation process!", quote=True)
        return True
    else:
        return False
