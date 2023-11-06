from pyrogram import filters

from MerissaRobot import pbot as app


@app.on_message(filters.command("donate"))
async def makeqr(c, m):
    amount = await m.chat.ask(
        "Please Enter amount you want to Donate", filters=filters.text
    )
    if int(amount.text) < 10:
        return await m.reply_text("Min. Donation amount is 10rs")
    url = f"https://pay.princexd.tech/prajapatiprince@apl/{amount.text}"
    button = InlineKeyboardMarkup([[InlineKeyboardButton("Pay", url=url), InlineKeyboardButton("Done ✅", callback_data="donated")]])
    x = f"Merissa UPI Payment - SCAN & PAY 📃 \n\nAmount: ₹{amount.text}\nMethod: UPI\n\nInstructions: Click below 'Pay' button to pay payment, after paying just comeback and click on 'done' button!"
    await m.reply_text(x, caption=f"<b>Thanks For Your donation</b>", reply_markup=button, quote=True)
