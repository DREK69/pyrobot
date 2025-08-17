import re
import time

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, CommandHandler, filters

from MerissaRobot import OWNER_ID, application
from MerissaRobot.Modules.disable import DisableAbleCommandHandler

# Get job queue from application
job_queue = application.job_queue


def get_time(time_str: str) -> int:
    """Convert time string to seconds"""
    if time_str[-1] == "s":
        return int(time_str[:-1])
    if time_str[-1] == "m":
        return int(time_str[:-1]) * 60
    if time_str[-1] == "h":
        return int(time_str[:-1]) * 3600
    if time_str[-1] == "d":
        return int(time_str[:-1]) * 86400


reminder_message = """
Your reminder:
{reason}
<i>Which you timed {time} before in {title}</i>
"""


async def reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's current reminders"""
    user = update.effective_user
    msg = update.effective_message
    jobs = job_queue.jobs()
    user_reminders = [job.name[1:] for job in jobs if job.name.endswith(str(user.id))]

    if not user_reminders:
        await msg.reply_text(
            text="You don't have any reminders set or all the reminders you have set have been completed",
            reply_to_message_id=msg.message_id,
        )
        return
    
    reply_text = "Your reminders (<i>Mentioned below are the <b>Timestamps</b> of the reminders you have set</i>):\n"
    for i, u in enumerate(user_reminders):
        reply_text += f"\n{i+1}. <code>{u}</code>"
    
    await msg.reply_text(
        text=reply_text, 
        reply_to_message_id=msg.message_id, 
        parse_mode=ParseMode.HTML
    )


async def set_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set a new reminder"""
    user = update.effective_user
    msg = update.effective_message
    chat = update.effective_chat
    reason = msg.text.split()
    
    if len(reason) == 1:
        await msg.reply_text(
            "No time and reminder to mention!", 
            reply_to_message_id=msg.message_id
        )
        return
    
    if len(reason) == 2:
        await msg.reply_text(
            "Nothing to reminder! Add a reminder", 
            reply_to_message_id=msg.message_id
        )
        return
    
    t = reason[1].lower()
    if not re.match(r"[0-9]+(d|h|m|s)", t):
        await msg.reply_text(
            "Use a correct format of time!", 
            reply_to_message_id=msg.message_id
        )
        return

    async def job(context: ContextTypes.DEFAULT_TYPE):
        """Job function to send reminder"""
        title = ""
        if chat.type == "private":
            title += "this chat"
        else:
            title += chat.title
        
        await context.bot.send_message(
            chat_id=user.id,
            text=reminder_message.format(
                reason=" ".join(reason[2:]), 
                time=t, 
                title=title
            ),
            disable_notification=False,
            parse_mode=ParseMode.HTML,
        )

    job_time = time.time()
    job_name = f"t{job_time}{user.id}".replace(".", "")
    
    job_queue.run_once(
        callback=job, 
        when=get_time(t), 
        name=job_name,
        user_id=user.id,
        chat_id=chat.id
    )
    
    await msg.reply_text(
        text="Your reminder has been set after {time} from now!\nTimestamp: <code>{time_stamp}</code>".format(
            time=t, 
            time_stamp=str(job_time).replace(".", "") + str(user.id)
        ),
        reply_to_message_id=msg.message_id,
        parse_mode=ParseMode.HTML,
    )


async def clear_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear a specific reminder by timestamp"""
    user = update.effective_user
    msg = update.effective_message
    text = msg.text.split()
    
    if len(text) == 1 or not re.match(r"[0-9]+", text[1]):
        await msg.reply_text(
            text="No/Wrong timestamp mentioned", 
            reply_to_message_id=msg.message_id
        )
        return
    
    if not text[1].endswith(str(user.id)):
        await msg.reply_text(
            text="The timestamp mentioned is not your reminder!",
            reply_to_message_id=msg.message_id,
        )
        return
    
    jobs = job_queue.get_jobs_by_name(f"t{text[1]}")
    if not jobs:
        await msg.reply_text(
            text="This reminder is already completed or either not set",
            reply_to_message_id=msg.message_id,
        )
        return
    
    jobs[0].schedule_removal()
    await msg.reply_text(
        text="Done cleared the reminder!", 
        reply_to_message_id=msg.message_id
    )


async def clear_all_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear all reminders (owner only)"""
    user = update.effective_user
    msg = update.effective_message
    
    if user.id != OWNER_ID:
        await msg.reply_text(
            text="Who this guy not being the owner wants me clear all the reminders!!?",
            reply_to_message_id=msg.message_id,
        )
        return
    
    jobs = list(job_queue.jobs())
    unremoved_reminders = []
    
    for job in jobs:
        try:
            job.schedule_removal()
        except Exception:
            unremoved_reminders.append(job.name[1:])
    
    reply_text = "Done cleared all the reminders!\n\n"
    if unremoved_reminders:
        reply_text += "Except (<i>Time stamps have been mentioned</i>):"
        for i, u in enumerate(unremoved_reminders):
            reply_text += f"\n{i+1}. <code>{u}</code>"
    
    await msg.reply_text(
        text=reply_text, 
        reply_to_message_id=msg.message_id, 
        parse_mode=ParseMode.HTML
    )


async def clear_all_my_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear all user's reminders"""
    user = update.effective_user
    msg = update.effective_message
    jobs = list(job_queue.jobs())
    
    if not jobs:
        await msg.reply_text(
            text="You don't have any reminders!", 
            reply_to_message_id=msg.message_id
        )
        return
    
    unremoved_reminders = []
    user_jobs_found = False
    
    for job in jobs:
        if job.name.endswith(str(user.id)):
            user_jobs_found = True
            try:
                job.schedule_removal()
            except Exception:
                unremoved_reminders.append(job.name[1:])
    
    if not user_jobs_found:
        await msg.reply_text(
            text="You don't have any reminders!", 
            reply_to_message_id=msg.message_id
        )
        return
    
    reply_text = "Done cleared all your reminders!\n\n"
    if unremoved_reminders:
        reply_text += "Except (<i>Time stamps have been mentioned</i>):"
        for i, u in enumerate(unremoved_reminders):
            reply_text += f"\n{i+1}. <code>{u}</code>"
    
    await msg.reply_text(
        text=reply_text, 
        reply_to_message_id=msg.message_id, 
        parse_mode=ParseMode.HTML
    )


def register_handlers():
    """Register all reminder handlers"""
    
    reminders_handler = CommandHandler(
        ["reminders", "myreminders"],
        reminders,
        filters=filters.ChatType.PRIVATE,
        block=False,
    )
    
    set_reminder_handler = DisableAbleCommandHandler(
        "setreminder", 
        set_reminder, 
        block=False
    )
    
    clear_reminder_handler = DisableAbleCommandHandler(
        "clearreminder", 
        clear_reminder, 
        block=False
    )
    
    clear_all_reminders_handler = CommandHandler(
        "clearallreminders",
        clear_all_reminders,
        filters=filters.Chat(OWNER_ID),
        block=False,
    )
    
    clear_all_my_reminders_handler = CommandHandler(
        ["clearmyreminders", "clearallmyreminders"],
        clear_all_my_reminders,
        filters=filters.ChatType.PRIVATE,
        block=False,
    )

    application.add_handler(reminders_handler)
    application.add_handler(set_reminder_handler)
    application.add_handler(clear_reminder_handler)
    application.add_handler(clear_all_reminders_handler)
    application.add_handler(clear_all_my_reminders_handler)


__mod_name__ = "Reminder ⏰"
__help__ = """
❂ /reminders*:* get a list of *TimeStamps* of your reminders. 
❂ /setreminder <time> <remind message>*:* Set a reminder after the mentioned time.
❂ /clearreminder <timestamp>*:* clears the reminder with that timestamp if the time to remind is not yet completed.
❂ /clearmyreminders*:* clears all the reminders of the user.
  
*Similar Commands:*
❂ /reminders | /myreminders
❂ /clearmyreminders | /clearallmyreminders
  
*Usage:*
❂ /setreminder 30s reminder*:* Here the time format is same as the time format in muting but with extra seconds(s)
❂ `/clearreminder 1234567890123456789`
"""

