from pyrogram import filters

from MerissaRobot import pbot as app
from MerissaRobot.helpers import getreq


@app.on_message(filters.command("donate"))
async def makeqr(c, m):
    amount = await m.chat.ask(
        "Please Enter amount you want to Donate", filters=filters.text
    )
    if int(amount.text) < 10:
        return await m.reply_text("Min. Donation amount is 10rs")
    teks = f"upi://pay?pa=prajapatiprince3011@paytm&pn=PrajapatiPrince&cu=INR&am={amount.text}"
    url = await getreq(f"https://api.princexd.tech/qrcode?text={teks}")
    await m.reply_photo(
        url["url"], caption=f"<b>Thanks For Your donation</b>", quote=True
    )
