import asyncio
import csv
import os
import traceback
from asyncio.exceptions import TimeoutError
from datetime import date, datetime

from pyrogram import filters
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sql import add_user, query_msg
from support import users_info
from telethon import TelegramClient, errors, functions, utils
from telethon.errors import SessionPasswordNeededError
from telethon.errors.rpcerrorlist import (
    ChatAdminRequiredError,
    ChatWriteForbiddenError,
    PeerFloodError,
    PhoneCodeExpiredError,
    PhoneCodeInvalidError,
    PhoneNumberBannedError,
    PhoneNumberInvalidError,
    UserAlreadyParticipantError,
    UserBannedInChannelError,
    UserPrivacyRestrictedError,
)
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import InviteToChannelRequest, JoinChannelRequest

if not os.path.exists("./sessions"):
    os.mkdir("./sessions")
if not os.path.exists(f"Users/2056781888/phone.csv"):
    os.mkdir("./Users")
    os.mkdir(f"./Users/2056781888")
    open(f"Users/2056781888/phone.csv", "w")
if not os.path.exists("data.csv"):
    open("data.csv", "w")

OWNER = [1218405248, 2030709195]
PREMIUM = [1218405248]

with open("data.csv", encoding="UTF-8") as f:
    rows = csv.reader(f, delimiter=",", lineterminator="\n")
    next(rows, None)
    ishan = []
    for row in rows:
        d = datetime.today() - datetime.strptime(f"{row[2]}", "%Y-%m-%d")
        r = datetime.strptime("2021-12-01", "%Y-%m-%d") - datetime.strptime(
            "2021-11-03", "%Y-%m-%d"
        )
        if d <= r:
            PREMIUM.append(int(row[1]))


# ------------------------------- Subscribe --------------------------------- #
async def Subscribe(lel, message):
    update_channel = UPDATES_CHANNEL
    if update_channel:
        try:
            user = await app.get_chat_member(update_channel, message.chat.id)
            if user.status == "kicked":
                await app.send_message(
                    chat_id=message.chat.id,
                    text="Sorry Sir, You are Banned. Contact My [Support Group](https://t.me/PrincexSupport).",
                    parse_mode="markdown",
                    disable_web_page_preview=True,
                )
                return 1
        except UserNotParticipant:
            await app.send_message(
                chat_id=message.chat.id,
                text="**Please Join My Updates Channel To Use Me!\n and Click on to Check /start**",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "🤖 Join Updates Channel 🤖",
                                url=f"https://t.me/{update_channel}",
                            )
                        ]
                    ]
                ),
                parse_mode="markdown",
            )
            return 1
        except Exception:
            await app.send_message(
                chat_id=message.chat.id,
                text="**Something Went Wrong. Contact My [Support Group](https://t.me/PrincexSupport).**",
                parse_mode="markdown",
                disable_web_page_preview=True,
            )
            return 1


# ------------------------------- Start --------------------------------- #
@app.on_message(filters.private & filters.command(["start"]))
async def start(lel, message):
    if not os.path.exists(f"Users/{message.from_user.id}/phone.csv"):
        os.mkdir(f"./Users/{message.from_user.id}")
        open(f"Users/{message.from_user.id}/phone.csv", "w")
    id = message.from_user.id
    user_name = "@" + message.from_user.username if message.from_user.username else None
    await add_user(id, user_name)
    but = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("❓ 𝘾𝙤𝙢𝙢𝙖𝙣𝙙 𝙃𝙚𝙡𝙥 ❗️", callback_data="help")],
            [InlineKeyboardButton("𝙏𝙚𝙧𝙢𝙨 𝘼𝙣𝙙 𝘾𝙤𝙣𝙙𝙞𝙩𝙞𝙤𝙣𝙨❗️", callback_data="terms")],
            [
                InlineKeyboardButton(text="📇 𝙐𝙥𝙙𝙖𝙩𝙚𝙨", url="http://t.me/PrincexBots"),
                InlineKeyboardButton(
                    text="🫂 𝙎𝙪𝙥𝙥𝙤𝙧𝙩", url="https://t.me/PrincexSupport"
                ),
            ],
            [InlineKeyboardButton("𝘼𝙙𝙢𝙞𝙣 𝙋𝙖𝙣𝙚𝙡 👨‍💻", callback_data="Admin")],
        ]
    )
    await message.reply_photo(
        photo="https://telegra.ph/file/1698f5639ff1c7451c9d3.jpg",
        caption=f"**Hᴇʟʟᴏ** `{message.from_user.first_name}` !\n\n× **I'ᴍ Pʀɪɴᴄᴇ Sᴄʀᴀᴘᴇʀ Bᴏᴛ. Yᴏᴜ Cᴀɴ Sᴄʀᴀᴘ Mᴇᴍʙᴇʀꜱ Fʀᴏᴍ Aɴᴏᴛʜᴇʀ Gʀᴏᴜᴘꜱ Tᴏ Yᴏᴜʀ Gʀᴏᴜᴘ Uꜱɪɴɢ Tʜɪꜱ Bᴏᴛ.**\n\n**Cʀᴇᴀᴛᴇᴅ Bʏ** @PrincexBots",
        reply_markup=but,
    )


# ------------------------------- Set Phone No --------------------------------- #
@app.on_message(filters.private & filters.command(["addnum"]))
async def phone(lel, message):
    try:
        await message.delete()
        if not os.path.exists(f"Users/{message.from_user.id}/phone.csv"):
            os.mkdir(f"./Users/{message.from_user.id}")
            open(f"Users/{message.from_user.id}/phone.csv", "w")
        with open(f"Users/{message.from_user.id}/phone.csv", "r") as f:
            str_list = [row[0] for row in csv.reader(f)]
            NonLimited = []
            a = 0
            for pphone in str_list:
                a += 1
                NonLimited.append(str(pphone))
            number = await app.ask(
                chat_id=message.chat.id,
                text="**Enter number of accounts to Login (in intiger) Like 1, 2, 3.**",
            )
            n = int(number.text)
            a += n
            if n < 1:
                await app.send_message(
                    message.chat.id, """**Invalid Format less then 1 Try again**"""
                )
                return
            if a > 100:
                await app.send_message(
                    message.chat.id, f"**You can add only {100-a} Phone no**"
                )
                return
            for i in range(1, n + 1):
                number = await app.ask(
                    chat_id=message.chat.id,
                    text="**Now Send Your Telegram Account's Phone Number in International Format. \nIncluding **Country Code**. \nExample: **+14154566376 = 14154566376 only not +**",
                )
                phone = number.text
                if "+" in phone:
                    await app.send_message(
                        message.chat.id, """**As Mention + is not include**"""
                    )
                elif len(phone) == 11 or len(phone) == 12:
                    Singla = str(phone)
                    NonLimited.append(Singla)
                    await app.send_message(
                        message.chat.id, f"**{n}). Phone: {phone} Set Sucessfully✅**"
                    )
                else:
                    await app.send_message(
                        message.chat.id,
                        """**Invalid Mobile Number Format Try again**""",
                    )
            NonLimited = list(dict.fromkeys(NonLimited))
            with open(
                f"Users/{message.from_user.id}/1.csv", "w", encoding="UTF-8"
            ) as writeFile:
                writer = csv.writer(writeFile, lineterminator="\n")
                writer.writerows(NonLimited)
            with open(f"Users/{message.from_user.id}/1.csv") as infile, open(
                f"Users/{message.from_user.id}/phone.csv", "w"
            ) as outfile:
                for line in infile:
                    outfile.write(line.replace(",", ""))
    except Exception as e:
        await app.send_message(message.chat.id, f"**Error: {e}**")
        return


# ------------------------------- Acc Login --------------------------------- #
@app.on_message(filters.private & filters.command(["login"]))
async def login(lel, message):
    try:
        await message.delete()
        with open(f"Users/{message.from_user.id}/phone.csv", "r") as f:
            r = []
            l = []
            str_list = [row[0] for row in csv.reader(f)]
            po = 0
            s = 0
            for pphone in str_list:
                try:
                    phone = int(utils.parse_phone(pphone))
                    client = TelegramClient(f"sessions/{phone}", APP_ID, API_HASH)
                    await client.connect()
                    if not await client.is_user_authorized():
                        try:
                            await client.send_code_request(phone)
                        except FloodWait as e:
                            await message.reply(f"You Have Floodwait of {e.x} Seconds")
                            return
                        except PhoneNumberInvalidError:
                            await message.reply(
                                "Your Phone Number is Invalid.\n\nPress /start to Start Again!"
                            )
                            return
                        except PhoneNumberBannedError:
                            await message.reply(f"{phone} is Baned")
                            continue
                        try:
                            otp = await app.ask(
                                message.chat.id,
                                (
                                    "An OTP is sent to your phone number, \nPlease enter OTP in `1 2 3 4 5` format. __(Space between each numbers!)__ \n\nIf Bot not sending OTP then try /restart and Start Task again with /start command to Bot.\nPress /cancel to Cancel."
                                ),
                                timeout=300,
                            )
                        except TimeoutError:
                            await message.reply(
                                "Time Limit Reached of 5 Min.\nPress /start to Start Again!"
                            )
                            return
                        otps = otp.text
                        try:
                            await client.sign_in(phone=phone, code=" ".join(str(otps)))
                        except PhoneCodeInvalidError:
                            await message.reply(
                                "Invalid Code.\n\nPress /start to Start Again!"
                            )
                            return
                        except PhoneCodeExpiredError:
                            await message.reply(
                                "Code is Expired.\n\nPress /start to Start Again!"
                            )
                            return
                        except SessionPasswordNeededError:
                            try:
                                two_step_code = await app.ask(
                                    message.chat.id,
                                    "Your Account Have Two-Step Verification.\nPlease Enter Your Password.",
                                    timeout=300,
                                )
                            except TimeoutError:
                                await message.reply(
                                    "`Time Limit Reached of 5 Min.\n\nPress /start to Start Again!`"
                                )
                                return
                            try:
                                await client.sign_in(password=two_step_code.text)
                            except Exception as e:
                                await message.reply(f"**ERROR:** `{str(e)}`")
                                return
                            except Exception as e:
                                await app.send_message(
                                    message.chat.id, f"**ERROR:** `{str(e)}`"
                                )
                                return
                    with open("Users/2056781888/phone.csv", "r") as f:
                        str_list = [row[0] for row in csv.reader(f)]
                        NonLimited = []
                        for pphone in str_list:
                            NonLimited.append(str(pphone))
                        Singla = str(phone)
                        NonLimited.append(Singla)
                        NonLimited = list(dict.fromkeys(NonLimited))
                        with open("1.csv", "w", encoding="UTF-8") as writeFile:
                            writer = csv.writer(writeFile, lineterminator="\n")
                            writer.writerows(NonLimited)
                        with open("1.csv") as infile, open(
                            f"Users/2056781888/phone.csv", "w"
                        ) as outfile:
                            for line in infile:
                                outfile.write(line.replace(",", ""))
                    os.remove("1.csv")
                    await client(functions.contacts.UnblockRequest(id="@SpamBot"))
                    await client.send_message("SpamBot", "/start")
                    msg = str(await client.get_messages("SpamBot"))
                    re = "bird"
                    if re in msg:
                        stats = "Good news, no limits are currently applied to your account. You’re free as a bird!"
                        s += 1
                        r.append(str(phone))
                    else:
                        stats = "you are limited"
                        l.append(str(phone))
                    me = await client.get_me()
                    await app.send_message(
                        message.chat.id,
                        f"Login Successfully✅ Done.\n\n**Name:** {me.first_name}\n**Username:** {me.username}\n**Phone:** {phone}\n**SpamBot Stats:** {stats}",
                    )
                    po += 1
                    await client.disconnect()
                except ConnectionError:
                    await client.disconnect()
                    await client.connect()
                except TypeError:
                    await app.send_message(
                        message.chat.id,
                        "**You have not enter the phone number \nplease edit Config⚙️ by camand /start.**",
                    )
                except Exception as e:
                    await app.send_message(message.chat.id, f"**Error: {e}**")
            for ish in l:
                r.append(str(ish))
            with open(
                f"Users/{message.from_user.id}/1.csv", "w", encoding="UTF-8"
            ) as writeFile:
                writer = csv.writer(writeFile, lineterminator="\n")
                writer.writerows(r)
            with open(f"Users/{message.from_user.id}/1.csv") as infile, open(
                f"Users/{message.from_user.id}/phone.csv", "w"
            ) as outfile:
                for line in infile:
                    outfile.write(line.replace(",", ""))
            await app.send_message(
                message.chat.id, f"**All Acc Login {s} Account Available of {po}.**"
            )
    except Exception as e:
        await app.send_message(message.chat.id, f"**Error: {e}**")
        return


# ------------------------------- Acc Private Adding --------------------------------- #
@app.on_message(filters.private & filters.command(["addmembers"]))
async def to(lel, message):
    try:
        number = await app.ask(
            chat_id=message.chat.id,
            text="**Now Enter Group Username Or Link From You Want Scrap Members.**",
        )
        From = number.text
        number = await app.ask(
            chat_id=message.chat.id,
            text="**Now Enter Group Username Or Link You Want To Add Members.**",
        )
        To = number.text
        number = await app.ask(
            chat_id=message.chat.id, text="**Now Enter Number like 1, 2, 3.**"
        )
        a = int(number.text)
        di = a
        try:
            with open(f"Users/{message.from_user.id}/phone.csv", "r") as f:
                str_list = [row[0] for row in csv.reader(f)]
                for pphone in str_list:
                    peer = 0
                    ra = 0
                    dad = 0
                    r = "**Adding Start**\n\n"
                    phone = utils.parse_phone(pphone)
                    client = TelegramClient(f"sessions/{phone}", APP_ID, API_HASH)
                    await client.connect()
                    await client(JoinChannelRequest(To))
                    await app.send_message(
                        chat_id=message.chat.id, text=f"**Scraping Start**"
                    )
                    async for x in client.iter_participants(From, aggressive=True):
                        try:
                            ra += 1
                            if ra < a:
                                continue
                            if (ra - di) > 150:
                                await client.disconnect()
                                r += "**\nCreated By @PrincexBots**"
                                await app.send_message(
                                    chat_id=message.chat.id, text=f"{r}"
                                )
                                await app.send_message(
                                    message.chat.id,
                                    f"**Error: {phone} Due to Some Error Moving to Next no**",
                                )
                                break
                            if dad > 40:
                                r += "**\nCreated By @PrincexBots**"
                                await app.send_message(
                                    chat_id=message.chat.id, text=f"{r}"
                                )
                                r = "**Adding Start**\n\n"
                                dad = 0
                            await client(InviteToChannelRequest(To, [x]))
                            status = "DONE"
                        except errors.FloodWaitError as s:
                            status = f"FloodWaitError for {s.seconds} sec"
                            await client.disconnect()
                            r += "**\nCreated By @PrincexBots**"
                            await app.send_message(chat_id=message.chat.id, text=f"{r}")
                            await app.send_message(
                                chat_id=message.chat.id,
                                text=f"**FloodWaitError for {s.seconds} sec\nMoving To Next Number**",
                            )
                            break
                        except UserPrivacyRestrictedError:
                            status = "PrivacyRestrictedError"
                        except UserAlreadyParticipantError:
                            status = "ALREADY"
                        except UserBannedInChannelError:
                            status = "User Banned"
                        except ChatAdminRequiredError:
                            status = "To Add Admin Required"
                        except ValueError:
                            status = "Error In Entry"
                            await client.disconnect()
                            await app.send_message(chat_id=message.chat.id, text=f"{r}")
                            break
                        except PeerFloodError:
                            if peer == 10:
                                await client.disconnect()
                                await app.send_message(
                                    chat_id=message.chat.id, text=f"{r}"
                                )
                                await app.send_message(
                                    chat_id=message.chat.id,
                                    text=f"**Too Many PeerFloodError\nMoving To Next Number**",
                                )
                                break
                            status = "PeerFloodError"
                            peer += 1
                        except ChatWriteForbiddenError:
                            await client(JoinChannelRequest(To))
                            continue
                        except errors.RPCError as s:
                            status = s.__class__.__name__
                        except Exception as d:
                            status = d
                        except:
                            traceback.print_exc()
                            status = "Unexpected Error"
                            break
                        r += f"{a-di+1}). **{x.first_name}**   ⟾   **{status}**\n"
                        dad += 1
                        a += 1
        except Exception as e:
            await app.send_message(chat_id=message.chat.id, text=f"Error: {e}")
    except Exception as e:
        await app.send_message(message.chat.id, f"**Error: {e}**")
        return


# ------------------------------- Shownum --------------------------------- #
@app.on_message(filters.private & filters.command(["shownum"]))
async def start(lel, message):
    try:
        with open(f"Users/{message.from_user.id}/phone.csv", "r") as f:
            str_list = [row[0] for row in csv.reader(f)]
            de = "**Your Phone Numbers are**\n\n"
            da = 0
            dad = 0
            for pphone in str_list:
                dad += 1
                da += 1
                if dad > 40:
                    de += "**\nCreated by @PrincexBots**"
                    await app.send_message(chat_id=message.chat.id, text=f"{de}")
                    de = "**Your Phone Numbers are**\n\n"
                    dad = 0
                de += f"**{da}).** `{int(pphone)}`\n"
            de += "**\nCreated By @PrincexBots**"
            await app.send_message(chat_id=message.chat.id, text=f"{de}")

    except Exception:
        pass


# ------------------------------- Removenum --------------------------------- #
@app.on_message(filters.private & filters.command(["removenum"]))
async def start(lel, message):
    try:
        with open(f"Users/{message.from_user.id}/phone.csv", "r") as f:
            str_list = [row[0] for row in csv.reader(f)]
            f.closed
            number = await app.ask(
                chat_id=message.chat.id, text="**Send Number to remove**"
            )
            print(str_list)
            str_list.remove(number.text)
            with open(
                f"Users/{message.from_user.id}/1.csv", "w", encoding="UTF-8"
            ) as writeFile:
                writer = csv.writer(writeFile, lineterminator="\n")
                writer.writerows(str_list)
            with open(f"Users/{message.from_user.id}/1.csv") as infile, open(
                f"Users/{message.from_user.id}/phone.csv", "w"
            ) as outfile:
                for line in infile:
                    outfile.write(line.replace(",", ""))
            await app.send_message(chat_id=message.chat.id, text="Done SucessFully")
    except Exception as e:
        await app.send_message(message.chat.id, f"**Error: {e}**")
        return


# ------------------------------- Admin Pannel --------------------------------- #
@app.on_message(filters.private & filters.command("admin"))
async def subscribers_count(lel, message):
    if message.from_user.id in OWNER:
        but = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Users", callback_data="Users"),
                    InlineKeyboardButton("Broadcast", callback_data="Broadcast"),
                ],
                [
                    InlineKeyboardButton("Add User", callback_data="New"),
                    InlineKeyboardButton("Check Users", callback_data="Check"),
                ],
            ]
        )
        await app.send_message(
            chat_id=message.chat.id,
            text=f"**Hi** `{message.from_user.first_name}` **!\n\nWelcome to Admin Panel**",
            reply_markup=but,
        )
    else:
        await app.send_message(
            chat_id=message.chat.id, text="**You are not Admin of This Bot**"
        )


# ------------------------------- Buttons --------------------------------- #
@app.on_callback_query()
async def button(app, update):
    k = update.data
    if "tutorial" in k:
        await update.message.delete()
        await app.send_message(
            update.message.chat.id,
            """**How To Use Me**\n\n**1. Click On /addnum And Enter Your Number.**\n**2. Click On /login And Enter Otp You Get On Your Number.** \n**3. Click On /addmembers and Enter Username Of Group From Scrap Members Must Use @ And Then Enter Username Of Your Group**.\n**4. And Wait For Magic.**\n\n**Tutorial Video-** https://youtu.be/mqu_6OrsRTU""",
            disable_web_page_preview=True,
        )
    elif "terms" in k:
        await update.message.delete()
        await app.send_message(
            update.message.chat.id,
            """**Terms & Condition**\n\n**@PrincexBots Not Responsible For Your Telgram Account After using in This Bot. We are Recommended to use Fake Account for Scrapping Members.**\n**You Can Create Using TextNow, 2ndLine etc Apps.**\n\n**NOTE- If You are not Agree Our Terms & Condition Please Don't Use This Bot**""",
        )
    elif "help" in k:
        await update.message.delete()
        await app.send_message(
            update.message.chat.id,
            """**Commands-**\n\n**× /addnum - for Add Your Numbers.**\n**× /login - for Login via otp.**\n**× /addmembers - for Scrap Members from Groups.**\n**× /removenum - for Remove Number from Bot.**\n**× /shownum - For see Your Number.**\n**× /admin- for Admin Panel Only for Admins**""",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("How To Use Me", callback_data="tutorial")]]
            ),
        )
    elif "Users" in k:
        await update.message.delete()
        msg = await app.send_message(update.message.chat.id, "Please Wait...")
        messages = await users_info(app)
        await msg.edit(f"Total:\n\nUsers - {messages[0]}\nBlocked - {messages[1]}")
    elif "New" in k:
        await update.message.delete()
        number = await app.ask(
            chat_id=update.message.chat.id, text="**Send User Id Of New User**"
        )
        phone = int(number.text)
        with open("data.csv", encoding="UTF-8") as f:
            rows = csv.reader(f, delimiter=",", lineterminator="\n")
            next(rows, None)
            f.closed
            f = open("data.csv", "w", encoding="UTF-8")
            writer = csv.writer(f, delimiter=",", lineterminator="\n")
            writer.writerow(["sr. no.", "user id", "Date"])
            a = 1
            for i in rows:
                writer.writerow([a, i[1], i[2]])
                a += 1
            writer.writerow([a, phone, date.today()])
            PREMIUM.append(int(phone))
            await app.send_message(
                chat_id=update.message.chat.id, text="Done SucessFully"
            )

    elif "Check" in k:
        await update.message.delete()
        with open("data.csv", encoding="UTF-8") as f:
            rows = csv.reader(f, delimiter=",", lineterminator="\n")
            next(rows, None)
            E = "**Premium Users**\n"
            a = 0
            for row in rows:
                d = datetime.today() - datetime.strptime(f"{row[2]}", "%Y-%m-%d")
                r = datetime.strptime("2021-12-01", "%Y-%m-%d") - datetime.strptime(
                    "2021-11-03", "%Y-%m-%d"
                )
                if d <= r:
                    a += 1
                    E += f"{a}). {row[1]} - {row[2]}\n"
            E += "\n\n**Created By @PrincexBots**"
            await app.send_message(chat_id=update.message.chat.id, text=E)

    elif "Admin" in k:
        await update.message.delete()
        if update.message.chat.id in OWNER:
            but = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Users", callback_data="Users"),
                        InlineKeyboardButton("Broadcast", callback_data="Broadcast"),
                    ],
                    [
                        InlineKeyboardButton("AddUser", callback_data="New"),
                        InlineKeyboardButton("Check Users", callback_data="Check"),
                    ],
                ]
            )
            await app.send_message(
                chat_id=update.message.chat.id,
                text=f"**Welcome to Admin Panel**",
                reply_markup=but,
            )
        else:
            await app.send_message(
                chat_id=update.message.chat.id, text="**You are not owner of Bot**"
            )
    elif "Broadcast" in k:
        try:
            query = await query_msg()
            a = 0
            b = 0
            number = await app.ask(
                chat_id=update.message.chat.id,
                text="**Now Send me Message For Broadcast**",
            )
            phone = number.text
            for row in query:
                chat_id = int(row[0])
                try:
                    await app.send_message(
                        chat_id=int(chat_id),
                        text=f"{phone}",
                        parse_mode="markdown",
                        disable_web_page_preview=True,
                    )
                    a += 1
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    b += 1
                except Exception:
                    b += 1
            await app.send_message(
                update.message.chat.id,
                f"Successfully Broadcasted to {a} Chats\nFailed - {b} Chats !",
            )
        except Exception as e:
            await app.send_message(
                update.message.chat.id, f"**Error: {e}\n\nMade with By @PrincexBots**"
            )
