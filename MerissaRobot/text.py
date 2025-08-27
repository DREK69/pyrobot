from telegram import InlineKeyboardButton, InlineKeyboardMarkup

PM_START_TEXT = """Hi Dear! My name is Merissa 👱‍♀[ ](https://te.legra.ph/file/90b1aa10cf8b77d5b781b.jpg)
──────────────────────
I can help to manage your groups with useful features, feel free to add me to your groups!
"""

PM_START_BUTTON = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                text="✚ Add Me To Your Group ✚",
                url="https://t.me/MerissaRobot?startgroup=new",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Help ❓",
                callback_data="help_back",
            ),
            InlineKeyboardButton(
                text="👩‍💻 Info",
                callback_data="merissa_",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Developer🧑‍💻",
                url="https://t.me/DEPSTEY",   # ✅ fixed
            ),
            InlineKeyboardButton(
                text="🔗 Inline",
                switch_inline_query_current_chat="",
            ),
        ],
        [
            InlineKeyboardButton(
                text="How To Use Me ⁉️",
                callback_data="cb_howtouse",
            ),
        ],
    ]
)

PM_ABOUT_TEXT = """@MerissaRobot is one of the most powerful group management bot exist in telegram trusted by 100k+ of users & one thousands of groups all over the world

MerissaRobot project is developed by @NotReallyPrince with the help of many Open Source Projects.

Merissa was Online Since 22 April 2022 and Helped many Admins to keep their Groups Effectively

_Merissa's licensed under the GNU General Public License v3.0_

Lets Enjoy The MerissaRobot And Join Support Group @MerissaxSupport"""

PM_ABOUT_BUTTON = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                text="About 👩‍💻",
                callback_data="merissa_about",
            ),
            InlineKeyboardButton(
                text="💰 Donate",
                callback_data="merissa_donate",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Support 🫂",
                callback_data="merissa_support",
            ),
            InlineKeyboardButton(
                text="✔️ Updates",
                callback_data="merissa_latestup",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Website 🔗",
                url="https://merissabot.me",
            ),
        ],
        [
            InlineKeyboardButton(
                text="🔙 Back",
                callback_data="merissa_back",
            ),
        ],
    ]
)

PM_SUPPORT_TEXT = """*Merissarobot Support Chats*

Join My Support Group/Channel for see or report a problem on MerissaRobot."""

PM_SUPPORT_BUTTON = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                text="Support 🫂",
                url="t.me/MerissaxSupport",
            ),
            InlineKeyboardButton(
                text="🗂️ Updates",
                url="https://t.me/MerissaxUpdates",
            ),
        ],
        [
            InlineKeyboardButton(text="🔙 Back", callback_data="merissa_"),
        ],
    ]
)

PM_DONATE_TEXT = """So you want to donate? Amazing!
It took a lot of work for my creator to get me to where I am now - so if you have some money to spare, and want to show your support; Donate!
After all, server fees don't pay themselves - so every little helps! All donation money goes straight to funding the VPS, and of course, boosting morale - always nice to see my work is appreciated :)
You can donate on Upi [here](https://t.me/PrincexDonatebot), or if you want to Help support Contact Me [Here](https://t.me/MerissaxSupport).
Thank you for your generosity!"""

HELP_MODULE_TEXT = "──「 Help of {} 」── \n"
HELP_STRINGS = "Click on the button bellow to get description about specifics command."

GROUP_START_TEXT = "👋 Hi, I'm Merissa. Nice to meet You."

GROUP_START_BUTTON = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                text="🧑‍💻 Developer",
                url="https://t.me/DEPSTEY",   # ✅ fixed
            ),
            InlineKeyboardButton(
                text="Help ❓",
                callback_data="merissa_setting",
            ),
        ],
        [InlineKeyboardButton(text="Close ❌", callback_data="cbclose")],
    ]
)

GROUP_HELP_BUTTON = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                text="👤 Open in Private Chat",
                callback_data="merissa_private",
            ),
        ],
        [
            InlineKeyboardButton(text="👥 Open Here", callback_data="ghelp_back"),
        ],
    ]
)

MERISSA_VID = "https://telegra.ph/file/50a69f6e684653fd626f4.mp4"

MERISSA_UPDATE_TEXT = """──「 Merissa v3.0 Update 」──

- New Profile Picture
- Added ChatGpt + Ai
- Added Anime Gifs Like Kiss, Slap, Cry.
- Added Speach to Text
- Added YouTube Shorts, Video, Audio Downloader 
- Added Tiktok Video Downloader 
- Added Instagram Story, Reels, Post, IGTV Videos Downloader
- Added P-Hub Video Downloader 
- Added Pinterest Video Downloader
- Added Movie/Anime Downloader
- Added Tempmail Generator
- Remove Image Editor"""
