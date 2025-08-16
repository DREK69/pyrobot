from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, filters, ContextTypes
from telegram.helpers import escape_markdown, mention_markdown
from telegram.constants import ParseMode

from MerissaRobot import application
from MerissaRobot.Handler.ptb.chat_status import user_admin, user_admin_no_reply
from MerissaRobot.Modules.disable import DisableAbleCommandHandler


@user_admin
async def start_attendance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if ("flag" in context.chat_data) and (context.chat_data["flag"] == 1):
        await update.message.reply_text(
            "Please close the current attendance first",
        )
    elif ("flag" not in context.chat_data) or (context.chat_data["flag"] == 0):
        context.chat_data["flag"] = 1
        context.chat_data["attendees"] = {}
        context.chat_data["id"] = update.effective_chat.id
        keyboard = [
            [
                InlineKeyboardButton(
                    "✋ Present Sir",
                    callback_data="present",
                ),
            ],
            [
                InlineKeyboardButton(
                    "🗂️ End Attendance",
                    callback_data="end_attendance",
                ),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.chat_data["message"] = await update.message.reply_text(
            "Please mark your Attendance, It's Compulsory 👮‍♀️",
            reply_markup=reply_markup,
        )


async def mark_attendance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if str(update.effective_user.id) not in context.chat_data["attendees"].keys():
        context.chat_data["attendees"][
            update.effective_user.id
        ] = f"{escape_markdown(update.effective_user.full_name)}"
        await context.bot.answer_callback_query(
            callback_query_id=query.id,
            text="Your attendance has been Marked 📝",
            show_alert=True,
        )
    else:
        await context.bot.answer_callback_query(
            callback_query_id=query.id,
            text="Your Attendance is already Marked 🔐",
            show_alert=True,
        )
    await query.answer()


@user_admin_no_reply
async def end_attendance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if context.chat_data["id"] != update.effective_chat.id:
        return
    if len(context.chat_data["attendees"].items()) > 0:
        attendee_list = "\n- ".join(
            [
                mention_markdown(id, name)
                for id, name in context.chat_data["attendees"].items()
            ]
        )
        await context.bot.edit_message_text(
            text="Attendance is over. "
            + str(len(context.chat_data["attendees"]))
            + " member(s) marked attendance.\n"
            + "Here is the list:\n- "
            + attendee_list,
            chat_id=context.chat_data["message"].chat_id,
            message_id=context.chat_data["message"].message_id,
            parse_mode=ParseMode.MARKDOWN,
        )
    else:
        await context.bot.edit_message_text(
            text="Attendance is over. No one was present.",
            chat_id=context.chat_data["message"].chat_id,
            message_id=context.chat_data["message"].message_id,
        )
    context.chat_data["flag"] = 0
    context.chat_data["attendees"].clear()


@user_admin
async def end_attendance_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if ("flag" not in context.chat_data) or (context.chat_data["flag"] != 1):
        await update.message.reply_text(
            "No Attendance is going on.",
        )
    else:
        if context.chat_data["id"] != update.effective_chat.id:
            return
        if len(context.chat_data["attendees"].items()) > 0:
            attendee_list = "\n- ".join(
                [
                    mention_markdown(id, name)
                    for id, name in context.chat_data["attendees"].items()
                ]
            )
            await context.bot.edit_message_text(
                text="Attendance is over. "
                + str(len(context.chat_data["attendees"]))
                + " members marked attendance.\n"
                + "Here is the list:\n- "
                + attendee_list,
                chat_id=context.chat_data["message"].chat_id,
                message_id=context.chat_data["message"].message_id,
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            await context.bot.edit_message_text(
                text="Attendance is over. No one was present.",
                chat_id=context.chat_data["message"].chat_id,
                message_id=context.chat_data["message"].message_id,
            )
        context.chat_data["flag"] = 0
        context.chat_data["attendees"].clear()


START_ATTENDANCE_CMD = DisableAbleCommandHandler(
    "attendance", start_attendance, filters=filters.ChatType.GROUPS
)
MARK_ATTENDANCE = CallbackQueryHandler(mark_attendance, pattern="present")
END_ATTENDANCE = CallbackQueryHandler(end_attendance, pattern="end_attendance")
END_ATTENDANCE_CMD = DisableAbleCommandHandler(
    "attendancestop", end_attendance_cmd, filters=filters.ChatType.GROUPS
)

application.add_handler(START_ATTENDANCE_CMD)
application.add_handler(MARK_ATTENDANCE)
application.add_handler(END_ATTENDANCE)
application.add_handler(END_ATTENDANCE_CMD)


__command_list__ = ["attendance", "attendancestop"]
__handlers__ = [
    START_ATTENDANCE_CMD,
    MARK_ATTENDANCE,
    END_ATTENDANCE,
    END_ATTENDANCE_CMD,
]
