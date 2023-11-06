from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from MerissaRobot import pbot as app


@app.on_message(filters.command("donate") & filters.private)
async def makeqr(c, m):
    amount = await m.chat.ask(
        "💲 Enter the amount of donation\n\nMinimun amount ₹10!", filters=filters.text
    )
    if int(amount.text) < 10:
        return await m.reply_text("Min. Donation amount is 10rs")
    url = f"https://pay.princexd.tech/prajapatiprince3011@paytm/{amount.text}"
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Pay", url=url),
                InlineKeyboardButton("Done ✅", callback_data="donated"),
            ]
        ]
    )
    x = f"Merissa UPI Payment - SCAN & PAY 📃 \n\nAmount: ₹{amount.text}\nMethod: UPI\n\nInstructions: Click below 'Pay' button to pay payment, after paying just comeback and click on 'done' button!"
    await m.reply_text(x, reply_markup=button)


@app.on_callback_query(filters.regex("^donated"))
async def donate_cb(bot, query):
    await query.message.delete()
    return await query.message.reply_text("Thank You For Donating Us")
