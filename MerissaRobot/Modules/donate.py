from pyrogram import filters

from MerissaRobot import pbot as app
from MerissaRobot.helpers import postreq


@app.on_message(filters.command("donate"))
async def makeqr(c, m):
    amount = await m.chat.ask(
        "Please Enter amount you want to Donate", filters=filters.text
    )
    if int(amount.text) < 10:
        return await m.reply_text("Min. Donation amount is 10rs")
    url = f"https://pay.princexd.tech/prajapatiprince@apl/{amount.text}"
    x = f"Merissa UPI Payment - SCAN & PAY 📃 \n\nAmount: ₹{amount.text}\nMethod: UPI\n\nInstructions: Click below 'Pay' button to pay payment, after paying just comeback and click on 'done' button!"
    await m.reply_text(
        , caption=f"<b>Thanks For Your donation</b>", quote=True
    )
