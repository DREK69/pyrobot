from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.ext import CallbackContext, CallbackQueryHandler

from MerissaRobot import dispatcher
from MerissaRobot.Modules.misc import MARKDOWN_HELP
from MerissaRobot.Modules.welcome import WELC_HELP_TXT


def cb_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    update.effective_chat
    if query.data == "cb_":
        query.message.edit_text(text="hi", parse_mode=ParseMode.MARKDOWN)
    elif query.data == "cb_howtouse":
        query.message.edit_text(
            text="""Welcome to the Merissa Configuration Tutorial.

The first thing to do is to add Merissa to your group! For doing that, press the under button and select your group, then press "Done" to continue the tutorial.""",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "✚ Add Me To Your Group ✚",
                            url="t.me/MerissaRobot?startgroup=new",
                        )
                    ],
                    [
                        InlineKeyboardButton("🔙 Back", callback_data="merissa_back"),
                        InlineKeyboardButton("Done ✅", callback_data="cb_done"),
                    ],
                ]
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )
    elif query.data == "cb_done":
        query.message.edit_text(
            text="""Ok, well done!

Now for let me work correctly, you need to make me Admin of your Group!

To do that, follow this easy steps: 
▫️ Go to your group
▫️ Press the Group's name
▫️ Press Modify
▫️ Press on Administrator
▫️ Press Add Administrator
▫️ Press the Magnifying Glass
▫️ Search @MerissaRobot
▫️ Confirm""",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Tutorial Video 🎥", callback_data="cb_tutorial"
                        )
                    ],
                    [
                        InlineKeyboardButton("🔙 Back", callback_data="help_back"),
                        InlineKeyboardButton("Done ✅", callback_data="cb_done1"),
                    ],
                ]
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )
    elif query.data == "cb_tutorial":
        query.message.reply_video(
            video="https://te.legra.ph/file/fe561673c9f58e2a9889a.mp4",
            caption="""To add MerissaRobot in your chat, follow the steps shown in the video.""",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Done ✅", callback_data="cb_donet")]]
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )
        query.message.delete()
    elif query.data == "cb_done1":
        query.message.edit_text(
            text="""Excellent! 
Now the Bot is ready to use!

If You Need More Help Click on Below Button""",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Help Menu", callback_data="help_back")]]
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )
    elif query.data == "cb_donet":
        query.message.reply_text(
            text="""Excellent! 
Now the Bot is ready to use!

If You Need More Help Click on Below Button""",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Help Menu", callback_data="help_back")]]
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )
        query.message.delete()
    elif query.data == "cb_setup":
        query.message.edit_text(
            text="""──「 Help of Setup Assistant 」──
            
1.) first, add me to your group.

2.) then promote me as admin and give all permissions except anonymous admin.
   
3.) add @MerissaxPlugin to your group.
            
4.) turn on the video chat first before start to play music.
             
Lets Enjoy The Merissa Music And Join Support Group @MerissaxSupport""",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back", callback_data="help_back")]]
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )
    elif query.data == "cb_disable":
        query.message.edit_text(
            text="""──「 Help of Disabling ⛔️ Module 」── 

❂ /cmds: check the current status of disabled commands

Admins only:
❂ /enable <cmd name>: enable that command
❂ /disable <cmd name>: disable that command
❂ /enablemodule <module name>: enable all commands in that module
❂ /disablemodule <module name>: disable all commands in that module
❂ /listcmds: list all possible toggleable commands""",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back", callback_data="cb_admin")]]
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )
    elif query.data == "cb_filling":
        query.message.edit_text(
            text=WELC_HELP_TXT,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back", callback_data="cb_format")]]
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )
    elif query.data == "cb_format":
        query.message.edit_text(
            text="""──「 Help of Formatting 📑 Module 」── 

Merissa supports a large number of formatting options to make your messages more expressive. Take a look!""",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Markdown", callback_data="cb_markdown"),
                        InlineKeyboardButton("Filling", callback_data="cb_filling"),
                    ],
                    [InlineKeyboardButton("🔙 Back", callback_data="help_back")],
                ]
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )
    elif query.data == "cb_markdown":
        query.message.edit_text(
            text=MARKDOWN_HELP,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back", callback_data="cb_format")]]
            ),
            disable_web_page_preview=False,
        )
    elif query.data == "cb_lock":
        query.message.edit_text(
            text="""──「 Help of Locks 🔐 Module 」── 

Do stickers annoy you? or want to avoid people sharing links? or pictures? You're in the right place!
The locks module allows you to lock away some common items in the telegram world; the bot will automatically delete them!

❂ /locktypes: Lists all possible locktypes

Admins only:
❂ /lock <type>: Lock items of a certain type (not available in private)
❂ /unlock <type>: Unlock items of a certain type (not available in private)
❂ /locks: The current list of locks in this chat.

Locks can be used to restrict a group's users.

eg:
Locking urls will auto-delete all messages with urls, locking stickers will restrict all non-admin users from sending stickers, etc.
Locking bots will stop non-admins from adding bots to the chat.

Note:
❂ Unlocking permission info will allow members (non-admins) to change the group information, such as the description or the group name
❂ Unlocking permission pin will allow members (non-admins) to pinned a message in a group""",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back", callback_data="help_back")]]
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )
    elif query.data == "cb_approve":
        query.message.edit_text(
            text="""──「 Help of Approve Module 」── 

Sometimes, you might trust a user not to send unwanted content.
Maybe not enough to make them admin, but you might be ok with locks, blacklists, and antiflood not applying to them.
That's what approvals are for - approve of trustworthy users to allow them to send

Admin commands:
❂ /approval: Check a user's approval status in this chat.
❂ /approve: Approve of a user. Locks, blacklists, and antiflood won't apply to them anymore.
❂ /unapprove: Unapprove of a user. They will now be subject to locks, blacklists, and antiflood again.
❂ /approved: List all approved users.
❂ /unapproveall: Unapprove ALL users in a chat. This cannot be undone.""",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back", callback_data="cb_admin")]]
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )
    elif query.data == "cb_log":
        query.message.edit_text(
            text="""──「 Help of Log-Channel Module 」──

❂ /logchannel*:* Get log channel info
❂ /setlog*:* Set the log channel.
❂ /unsetlog*:* Unset the log channel.

*Setting the log channel is done by*:
➩ Adding the bot to the desired channel (as an admin!)
➩ Sending /setlog in the channel
➩ Forwarding the /setlog to the group""",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back", callback_data="cb_admin")]]
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )
    elif query.data == "cb_pin":
        query.message.edit_text(
            text="""──「 Help of Pin Module 」──

❂ /pin*:* silently pins the message replied to - add `'loud'` or `'notify'` to give notifs to users
❂ /unpin*:* unpins the currently pinned message
❂ /pinned*:* to get the current pinned message.""",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back", callback_data="cb_admin")]]
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )
    elif query.data == "cb_promote":
        query.message.edit_text(
            text="""──「 Help of Promote Module 」──

❂ /promote*:* promotes the replied to User
❂ /fullpromote*:* promotes the user replied to with full rights
❂ /demote*:* demotes the replied to User""",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back", callback_data="cb_admin")]]
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )
    elif query.data == "cb_group":
        query.message.edit_text(
            text="""──「 Help of Group Commands 」──

❂ /title <title here>*:* sets a custom title for an admin that the bot promoted
❂ /admincache*:* force refresh the admins list
❂ /del*:* deletes the message you replied to
❂ /purge*:* deletes all messages between this and the replied to message.
❂ /purge <integer X>*:* deletes the replied message, and X messages following it if replied to a message.
❂ /setgtitle <text>*:* set group title
❂ /setgpic*:* reply to an image to set as group photo
❂ /setdesc*:* Set group description
❂ /setsticker*:* Set group sticker""",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back", callback_data="cb_admin")]]
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )
    elif query.data == "cb_rules":
        query.message.edit_text(
            text="""──「 Help of Rules Module 」──

❂ /rules*:* get the rules for this chat.
❂ /setrules <your rules here>*:* set the rules for this chat.
❂ /clearrules*:* clear the rules for this chat.""",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back", callback_data="cb_admin")]]
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )
    elif query.data == "cb_antichannel":
        query.message.edit_text(
            text="""──「 Help of Anti-Channel Module 」──

Your groups to stop anonymous channels sending messages into your chats.

**Type of messages**
        - document
        - photo
        - sticker
        - animation
        - video
        - text
        
**Admin Commands:**
 - /antichannel [on / off] - Anti- channel  function 

**Note** : If linked channel send any containing characters in this type when on function no del    """,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back", callback_data="cb_admin")]]
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )
    elif query.data == "cb_flood":
        query.message.edit_text(
            text="""──「 Help of Anti-Spam Module 」──

❂ /antispam <on/off/yes/no>: Will toggle our antispam tech or return your current settings.
Anti-Spam, used by bot devs to ban spammers across all groups. This helps protect \
you and your groups by removing spam flooders as quickly as possible.

❂ /flood: Get the current antiflood settings
❂ /setflood <number/off/no>: Set the number of messages after which to take action on a user. Set to '0', 'off', or 'no' to disable.
❂ /setfloodmode <action type>: Choose which action to take on a user who has been flooding. Options: ban/kick/mute/tban/tmute

Note: Users can appeal gbans or report spammers at @MerissaxSupport""",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back", callback_data="help_back")]]
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )
    elif query.data == "cb_antilang":
        query.message.edit_text(
            text="""──「 Help of Anti-Language 」──

Delete messages containing characters from one of the following automatically
- Arabic Language
- Chinese Language
- Japanese Language (Includes Hiragana, Kanji and Katakana)
- Sinhala Language
- Tamil Language
- Cyrillic Language

Admin Commands:

- /antiarabic [on | off] -  anti-arab function
- /antichinese [on | off] -  anti-chinese function
- /antijapanese [on | off] -  anti-japanese function
- /antirussian [on | off] -  anti-russian function
- /antisinhala [on | off] -  anti-sinhala function
- /antitamil [on | off] -  anti-tamilfunction

Note : If admin send any containing characters in this lang when on  any function
it will delete and user send 3 warn and after ban him""",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back", callback_data="help_back")]]
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )
    elif query.data == "cb_service":
        query.message.edit_text(
            text="""──「 Help of Anti-Service Module 」──

I Can Remove Service Message In Groups 
Like Users Join Messages, Leave Messages, Pinned Allert Messages, 
Voice Chat Invite Members Allerts ETC..

- /antiservice [enable|disable]""",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back", callback_data="help_back")]]
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )
    elif query.data == "cb_fed":
        query.message.edit_text(
            text="""Ah, group management. It's all fun and games, until you start getting spammers in, and you need to ban them. Then you need to start banning more, and more, and it gets painful.
But then you have multiple groups, and you don't want these spammers in any of your groups - how can you deal? Do you have to ban them manually, in all your groups?
No more! With federations, you can make a ban in one chat overlap to all your other chats.
You can even appoint federation admins, so that your trustworthy admins can ban across all the chats that you want to protect.

Commands:
 - /newfed <fedname>: creates a new federation with the given name. Users are only allowed to own one federation. This method can also be used to change the federation name. (max 64 characters)
 - /delfed: deletes your federation, and any information relating to it. Will not unban any banned users.
 - /fedinfo <FedID>: information about the specified federation.
 - /joinfed <FedID>: joins the current chat to the federation. Only chat owners can do this. Each chat can only be in one federation.
 - /leavefed <FedID>: leaves the given federation. Only chat owners can do this.
 - /fpromote <user>: promotes the user to fed admin. Fed owner only.
 - /fdemote <user>: demotes the user from fed admin to normal user. Fed owner only.
 - /fban <user>: bans a user from all federations that this chat is in, and that the executor has control over.
 - /unfban <user>: unbans a user from all federations that this chat is in, and that the executor has control over.
 - /setfrules: Set federation rules
 - /frules: Show federation rules
 - /chatfed: Show the federation the chat is in
 - /fedadmins: Show the federation admins
""",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back", callback_data="cb_admin")]]
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )
    elif query.data == "cb_fsub":
        query.message.edit_text(
            text="""──「 Help of F-Sub Module 」── 
 
❂ /fsub {channel username} - To turn on and setup the channel.
  💡Do this first...
❂ /fsub - To get the current settings.
❂ /fsub disable - To turn of ForceSubscribe..
  💡If you disable fsub, you need to set again for working.. /fsub {channel username} 
❂ /fsub clear - To unmute all members who muted by me.

Force Subscribe:
❂ Merissa can mute members who are not subscribed your channel until they subscribe
❂ When enabled I will mute unsubscribed members and show them a unmute button. When they pressed the button I will unmute them
❂Setup
Only creator
❂ Add me in your group as admin
❂ Add me in your channel as admin""",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back", callback_data="cb_admin")]]
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )
    elif query.data == "cb_string":
        query.message.edit_text(
            text="""──「 Help of String-Gen Module 」──

❂ /start - Start the Bot
❂ /generate - Start Generating Session
❂ /about - About The Bot
❂ /help - This Message
❂ /cancel - Cancel the process
❂ /restart - Cancel the process""",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back", callback_data="cb_tool")]]
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )
    elif query.data == "cb_extra":
        query.message.edit_text(
            text="""──「 Help of Extra Module 」──

❂ /markdownhelp: quick summary of how markdown works in telegram - can only be called in private chats
❂ /paste: Saves replied content to nekobin.com and replies with a url
❂ /react: Reacts with a random reaction 
❂ /ud <word>: Type the word or expression you want to search use
❂ /reverse: Does a reverse image search of the media which it was replied to.
❂ /wiki <query>: wikipedia your query
❂ /wall <query>: get a wallpaper from wall.alphacoders.com
❂ /cash: currency converter
 Example:
 /cash 1 USD INR  
      OR
 /cash 1 usd inr
 Output: 1.0 USD = 75.505 INR""",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back", callback_data="cb_tool")]]
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )
    elif query.data == "cb_font":
        query.message.edit_text(
            text="""──「 Help of Font Module 」──

- Here is the help for the Styletext module:
❂ /weebify <text>: weebify your text!
❂ /bubble <text>: bubble your text!
❂ /fbubble <text>: bubble-filled your text!
❂ /square <text>: square your text!
❂ /fsquare <text>: square-filled your text!
❂ /blue <text>: bluify your text!
❂ /latin <text>: latinify your text!
❂ /lined <text>: lined your text!""",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back", callback_data="cb_tool")]]
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )
    elif query.data == "cb_toolb":
        query.message.edit_text(
            text="""──「 Help of Tools 🛠️ Module 」──

Here is the help for the tools module:
We promise to keep you latest up-date with the latest technology on telegram. 
we upgrade MerissaRobot everyday to simplifie use of telegram and give a better exprince to users.

Click on below buttons and check amazing tools for users.""",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Sangmata", callback_data="cb_sg"),
                        InlineKeyboardButton("Search", callback_data="cb_search"),
                        InlineKeyboardButton("Shippering", callback_data="cb_couple"),
                    ],
                    [
                        InlineKeyboardButton("Translate", callback_data="cb_translate"),
                        InlineKeyboardButton("Tagall", callback_data="cb_tagall"),
                        InlineKeyboardButton("Weather", callback_data="cb_weather"),
                    ],
                    [
                        InlineKeyboardButton("🔙 Back", callback_data="cb_tool"),
                        InlineKeyboardButton("Main Menu", callback_data="help_back"),
                    ],
                ]
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )
    elif query.data == "cb_tool":
        query.message.edit_text(
            text="""──「 Help of Tools 🛠️ Module 」──

Here is the help for the tools module:
We promise to keep you latest up-date with the latest technology on telegram. 
we upgrade MerissaRobot everyday to simplifie use of telegram and give a better exprince to users.

Click on below buttons and check amazing tools for users.""",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Afk", callback_data="cb_afk"),
                        InlineKeyboardButton("Animation", callback_data="cb_animation"),
                        InlineKeyboardButton("Anime", callback_data="cb_anime"),
                    ],
                    [
                        InlineKeyboardButton("Convert", callback_data="cb_convert"),
                        InlineKeyboardButton("Extra", callback_data="cb_extra"),
                        InlineKeyboardButton("Fun", callback_data="cb_fun"),
                    ],
                    [
                        InlineKeyboardButton("🔙 Back", callback_data="help_back"),
                        InlineKeyboardButton("➡️", callback_data="cb_toolb"),
                    ],
                ]
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )
    elif query.data == "cb_admin":
        query.message.edit_text(
            text="""──「 Help of Admin Module 」──

Here is the help for the Admin module:
We promise to keep you latest up-date with the latest technology on telegram. 
we upgrade MerissaRobot everyday to simplifie use of telegram and give a better exprince to users.

Click on below buttons and check Amazing Admin commands for Users""",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Approve", callback_data="cb_approve"),
                        InlineKeyboardButton("Disable", callback_data="cb_disable"),
                        InlineKeyboardButton("Group", callback_data="cb_group"),
                    ],
                    [
                        InlineKeyboardButton("F-Sub", callback_data="cb_fsub"),
                        InlineKeyboardButton("Feds", callback_data="cb_fed"),
                        InlineKeyboardButton("Lock", callback_data="cb_lock"),
                    ],
                    [
                        InlineKeyboardButton("🔙 Back", callback_data="help_back"),
                        InlineKeyboardButton("Next ➡️", callback_data="cb_adminb"),
                    ],
                ]
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )
    elif query.data == "cb_adminb":
        query.message.edit_text(
            text="""──「 Help of Admin Module 」──

Here is the help for the Admin module:
We promise to keep you latest up-date with the latest technology on telegram. 
we upgrade MerissaRobot everyday to simplifie use of telegram and give a better exprince to users.

Click on below buttons and check Amazing Admin commands for Users.""",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Log-Channel", callback_data="cb_log"),
                        InlineKeyboardButton("Pin", callback_data="cb_pin"),
                    ],
                    [
                        InlineKeyboardButton("Promote", callback_data="cb_promote"),
                        InlineKeyboardButton("Rules", callback_data="cb_rules"),
                    ],
                    [
                        InlineKeyboardButton("🔙 Back", callback_data="cb_admin"),
                        InlineKeyboardButton("Main Menu", callback_data="help_back"),
                    ],
                ]
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )
    elif query.data == "cb_sg":
        query.message.edit_text(
            text="""──「 Help of Name History Module 」──

❂ /sg <reply>*:* To check Name History Of any Telegram User.""",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back", callback_data="cb_tool")]]
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )
    elif query.data == "cb_search":
        query.message.edit_text(
            text="""──「 Help of Search Module 」──

❂ /google <query>*:* Perform a google search
❂ /image <query>*:* Search Google for images and returns them\nFor greater no. of results specify lim, For eg: `/img hello lim=10`
❂ /app <appname>*:* Searches for an app in Play Store and returns its details.
❂ /reverse: Does a reverse image search of the media which it was replied to.
❂ /gps <location>*:* Get gps location.
❂ /github <username>*:* Get information about a GitHub user.
❂ /country <country name>*:* Gathering info about given country
❂ /imdb <Movie name>*:* Get full info about a movie with imdb.com
❂ Merissa <query>*:* Merissa answers the query

💡Ex: `Merissa where is Japan?`""",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back", callback_data="cb_tool")]]
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )
    elif query.data == "cb_tagall":
        query.message.edit_text(
            text="""──「 Help of Tagall Module 」──

Merissa Can Be a Mention Bot for your group.

Only admins can tag all.  Here is a list of commands

❂ /tagall or @all (reply to message or add another message) To mention all members in your group, without exception.
❂ /cancel for canceling the mention-all.""",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back", callback_data="cb_tool")]]
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )
    elif query.data == "cb_weather":
        query.message.edit_text(
            text="""──「 Help of Whether Module 」──

❂ /time <country code>*:* Gives information about a timezone.
❂ /weather <city>*:* Get weather info in a particular place.
❂ /wttr <city>*:* Advanced weather module, usage same as /weather
❂ /wttr moon*:* Get the current status of moon""",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back", callback_data="cb_tool")]]
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )
    elif query.data == "cb_anime":
        query.message.edit_text(
            text="""──「 Anime search 」──    
                       
❂ /anime <anime>: returns information about the anime.
❂ /whatanime: returns source of anime when replied to photo or gif.                                                          
❂ /character <character>: returns information about the character.
❂ /manga <manga>: returns information about the manga.
❂ /user <user>: returns information about a MyAnimeList user.
❂ /upcoming: returns a list of new anime in the upcoming seasons.
❂ /airing <anime>: returns anime airing info.
❂ /whatanime <anime>: reply to gif or photo.
❂ /kaizoku <anime>: search an anime on animekaizoku.com
❂ /kayo <anime>: search an anime on animekayo.com

 ──「 Anime Quotes 」 ──
❂ /animequotes: for anime quotes randomly as photos.
❂ /quote: send quotes randomly as text""",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back", callback_data="cb_tool")]]
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )
    elif query.data == "cb_convert":
        query.message.edit_text(
            text="""──「 Help of Convert Module 」──

• Encrypt
❂ /encrypt*:* Encrypts The Given Text
❂ /decrypt*:* Decrypts Previously Ecrypted Text

• File To Link:
❂ /transfersh: reply to a telegram file to upload it on transfersh and get direct download link
❂ /tmpninja: reply to a telegram file to upload it on tmpninja and get direct download link
 
• File Or Text To Telegraph:
❂ /tgm : Get Telegraph Link Of Replied Media
❂ /tgt: Get Telegraph Link of Replied Text

• Link To File:
❂ /up: reply to a direct download link to upload it to telegram as files
 
• Zipper
❂ /zip*:* reply to a telegram file to compress it in .zip format
❂ /unzip*:* reply to a telegram file to decompress it from the .zip format""",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back", callback_data="cb_tool")]]
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )
    elif query.data == "cb_captcha":
        query.message.edit_text(
            text="""──「 Help of Captcha Module 」──
           
Some chats get a lot of users joining just to spam. This could be because they're trolls, or part of a spam network.
To slow them down, you could try enabling CAPTCHAs. New users joining your chat will be required to complete a test to confirm that they're real people.'
Admin commands:
- /captcha <yes/no/on/off>: All users that join will need to solve a CAPTCHA. This proves they aren't a bot!
- /captchamode <button/multibutton/math/text>: Choose which CAPTCHA type to use for your chat.
- /captcharules <yes/no/on/off>: Require new users accept the rules before being able to speak in the chat.
- /captchatime <Xw/d/h/m>: Unmute new users after X time. If a user hasn't solved the CAPTCHA yet, they get automatically unmuted after this period.
- /captchakick <yes/no/on/off>: Kick users that haven't solved the CAPTCHA.
- /captchakicktime <Xw/d/h/m>: Set the time after which to kick CAPTCHA'd users.
- /setcaptchatext <text>: Customise the CAPTCHA button.
- /resetcaptchatext: Reset the CAPTCHA button to the default text.
Examples:
- Enable CAPTCHAs
->` /captcha on`
- Change the CAPTCHA mode to text.
->` /captchamode text`
- Enable CAPTCHA rules, forcing users to read the rules before being allowed to speak.
->` /captcharules on`
NOTE:
captchakicktime now only accept time in Seconds, will fix soon.
captchas Work with or without welcome messages being set.
not finsihed writing.""",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back", callback_data="help_back")]]
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )
    elif query.data == "cb_afk":
        query.message.edit_text(
            text="""──「 Help of Afk Module 」──

When marked as AFK, any mentions will be replied to with a message stating that you're not available!
❂ /afk <reason>*:* Mark yourself as AFK.
  - brb <reason>: Same as the afk command, but not a command. 
""",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back", callback_data="cb_tool")]]
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )
    elif query.data == "cb_animation":
        query.message.edit_text(
            text="""──「 Help of Animation Module 」──

- Animation
❂ /love 
❂ /hack 
❂ /bombs """,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back", callback_data="cb_tool")]]
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )
    elif query.data == "cb_couple":
        query.message.edit_text(
            text="""──「 Help of Shippering Module 」──

- Shippering
❂ /couples - get couples of today""",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back", callback_data="cb_tool")]]
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )
    elif query.data == "cb_fun":
        query.message.edit_text(
            text="""──「 Help of Fun Module 」──

- Fun commands
❂ /runs*:* reply a random string from an array of replies
❂ /slap*:* slap a user, or get slapped if not a reply
❂ /shrug*:* get shrug XD
❂ /table*:* get flip/unflip :v
❂ /decide*:* Randomly answers yes/no/maybe
❂ /toss*:* Tosses A coin
❂ /bluetext*:* check urself :V
❂ /roll*:* Roll a dice
❂ /rlg*:* Join ears,nose,mouth and create an emo ;-;
❂ /shout <keyword>*:* write anything you want to give loud shout
❂ /weebify <text>*:* returns a weebified text
❂ /sanitize*:* always use this before /pat or any contact
❂ /pat*:* pats a user, or get patted
❂ /8ball*:* predicts using 8ball method
❂ /ptl or /asupan: get random video from Instagram timeline
❂ /chika: get random video from chikakiku
❂ /wibu:get random short anime video or photos
""",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back", callback_data="cb_tool")]]
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )
    elif query.data == "cb_translate":
        query.message.edit_text(
            text="""──「 Help of Translate Module 」──

Use this module to translate stuff!
*Commands:*
❂ /tl (or /tr): as a reply to a message, translates it to English.
❂ /tl <lang>: translates to <lang>
eg: /tl ja: translates to Japanese.
❂ /tl <source>//<dest>: translates from <source> to <lang>.
eg:  /tl ja//en: translates from Japanese to English.
❂ /langs: get a list of supported languages for translation.

I can convert text to voice and voice to text..
❂ /tts <lang code>*:* Reply to any message to get text to speech output
❂ /stt*:* Type in reply to a voice message(support english only) to extract text from it.
*Language Codes*
`af,am,ar,az,be,bg,bn,bs,ca,ceb,co,cs,cy,da,de,el,en,eo,es,
et,eu,fa,fi,fr,fy,ga,gd,gl,gu,ha,haw,hi,hmn,hr,ht,hu,hy,
id,ig,is,it,iw,ja,jw,ka,kk,km,kn,ko,ku,ky,la,lb,lo,lt,lv,mg,mi,mk,
ml,mn,mr,ms,mt,my,ne,nl,no,ny,pa,pl,ps,pt,ro,ru,sd,si,sk,sl,
sm,sn,so,sq,sr,st,su,sv,sw,ta,te,tg,th,tl,tr,uk,ur,uz,
vi,xh,yi,yo,zh,zh_CN,zh_TW,zu`""",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back", callback_data="cb_tool")]]
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )
    elif query.data == "cb_close":
        query.message.delete()


CB_HANDLER = CallbackQueryHandler(cb_callback, pattern="^cb_", run_async=True)
dispatcher.add_handler(CB_HANDLER)
