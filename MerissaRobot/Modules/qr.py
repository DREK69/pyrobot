import os
import cv2
import qrcode
from pyrogram import filters
from MerissaRobot import pbot


@pbot.on_message(filters.command("qr"))
async def qr(c, m):
    # --- Case 1: Agar text diya hai
    if " " in m.text:
        await m.reply_text("Plz wait bruh!!")
        text = str(m.text).split(" ", 1)[1]
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save("qr.png")
        try:
            await c.send_photo(m.chat.id, "qr.png")
        except:
            await c.send_document(m.chat.id, "qr.png")
        os.remove("qr.png")

    # --- Case 2: Agar reply ek text par hai
    elif m.reply_to_message and m.reply_to_message.text:
        text = m.reply_to_message.text
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save("qr.png")
        try:
            await c.send_photo(m.chat.id, "qr.png")
        except:
            await c.send_document(m.chat.id, "qr.png")
        os.remove("qr.png")

    # --- Case 3: Agar reply ek photo (QR code image) par hai
    elif m.reply_to_message and m.reply_to_message.photo:
        x = await m.reply_text("Processing QR scan...")
        try:
            d = cv2.QRCodeDetector()
            qr_code = await m.reply_to_message.download()
            val, p, s = d.detectAndDecode(cv2.imread(qr_code))
            if val:
                await x.edit(f"✅ QR Code Data: `{val}`")
            else:
                await x.edit("❌ No QR code found in image.")
            os.remove(qr_code)
        except Exception as e:
            await x.edit(f"Failed to get data: {e}")

    # --- Case 4: Empty command
    elif not m.reply_to_message:
        await m.reply(
            "❓ Usage:\n"
            "- `/qr your_text_here` → Generate QR code\n"
            "- Reply text with `/qr` → Generate QR\n"
            "- Reply QR image with `/qr` → Decode QR"
        )

    else:
        await m.reply("Unsupported!")
