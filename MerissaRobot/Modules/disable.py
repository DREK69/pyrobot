import importlib
from typing import Union

from telegram import Update
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    filters,
    MessageHandler,
)
from telegram.constants import ParseMode
from telegram.helpers import escape_markdown

from MerissaRobot import application
from MerissaRobot.Handler.ptb.handlers import CMD_STARTERS, SpamChecker
from MerissaRobot.Handler.ptb.misc import is_module_loaded

CMD_STARTERS = tuple(CMD_STARTERS)

FILENAME = __name__.rsplit(".", 1)[-1]

# If module is due to be loaded, then setup all the magical handlers
if is_module_loaded(FILENAME):
    from MerissaRobot.Database.sql import disable_sql as sql
    from MerissaRobot.Handler.ptb.chat_status import (
        connection_status,
        is_user_admin,
        user_admin,
    )

    DISABLE_CMDS = []
    DISABLE_OTHER = []
    ADMIN_CMDS = []

    class DisableAbleCommandHandler(CommandHandler):
        def __init__(self, command, callback, admin_ok=False, **kwargs):
            super().__init__(command, callback, **kwargs)
            self.admin_ok = admin_ok
            if isinstance(command, str):
                DISABLE_CMDS.append(command)
                if admin_ok:
                    ADMIN_CMDS.append(command)
            else:
                DISABLE_CMDS.extend(command)
                if admin_ok:
                    ADMIN_CMDS.extend(command)

        def check_update(self, update):
            if isinstance(update, Update) and update.effective_message:
                message = update.effective_message

                if message.text and len(message.text) > 1:
                    fst_word = message.text.split(None, 1)[0]
                    if len(fst_word) > 1 and any(
                        fst_word.startswith(start) for start in CMD_STARTERS
                    ):
                        args = message.text.split()[1:]
                        command = fst_word[1:].split("@")
                        command.append(message.bot.username)

                        if not (
                            command[0].lower() in self.command
                            and command[1].lower() == message.bot.username.lower()
                        ):
                            return None
                        
                        chat = update.effective_chat
                        user = update.effective_user
                        if user.id == 1087968824:
                            user_id = chat.id
                        else:
                            user_id = user.id
                            
                        if SpamChecker.check_user(user_id):
                            return None
                            
                        filter_result = self.filters.check_update(update) if self.filters else True
                        if filter_result:
                            # disabled, admincmd, user admin
                            if sql.is_command_disabled(chat.id, command[0].lower()):
                                # check if command was disabled
                                is_disabled = command[0] in ADMIN_CMDS and is_user_admin(chat, user.id)
                                if not is_disabled:
                                    return None
                                return args, filter_result

                            return args, filter_result
                        return False

    class DisableAbleMessageHandler(MessageHandler):
        def __init__(self, pattern, callback, friendly="", **kwargs):
            super().__init__(pattern, callback, **kwargs)
            DISABLE_OTHER.append(friendly)
            self.friendly = friendly
            if pattern:
                self.filters = filters.UpdateType.MESSAGE & pattern
            else:
                self.filters = filters.UpdateType.MESSAGE

        def check_update(self, update):
            chat = update.effective_chat
            message = update.effective_message
            filter_result = self.filters.check_update(update) if self.filters else True

            try:
                args = message.text.split()[1:] if message.text else []
            except:
                args = []

            if super().check_update(update):
                if sql.is_command_disabled(chat.id, self.friendly):
                    return False
                return args, filter_result

    class DisableAbleRegexHandler(MessageHandler):
        def __init__(self, pattern, callback, friendly="", filters_=None, **kwargs):
            # Convert regex pattern to MessageHandler with Regex filter
            regex_filter = filters.Regex(pattern)
            if filters_:
                combined_filter = regex_filter & filters_
            else:
                combined_filter = regex_filter
                
            super().__init__(combined_filter, callback, **kwargs)
            DISABLE_OTHER.append(friendly)
            self.friendly = friendly

        def check_update(self, update):
            chat = update.effective_chat
            if super().check_update(update):
                if sql.is_command_disabled(chat.id, self.friendly):
                    return False
                return True

    @connection_status
    @user_admin
    async def disable(update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        chat = update.effective_chat
        if len(args) >= 1:
            disable_cmd = args[0]
            if disable_cmd.startswith(CMD_STARTERS):
                disable_cmd = disable_cmd[1:]

            if disable_cmd in set(DISABLE_CMDS + DISABLE_OTHER):
                sql.disable_command(chat.id, str(disable_cmd).lower())
                await update.effective_message.reply_text(
                    f"✅ **Disabled** the use of `{disable_cmd}`",
                    parse_mode=ParseMode.MARKDOWN,
                )
            else:
                await update.effective_message.reply_text(
                    "❌ That command can't be disabled"
                )

        else:
            await update.effective_message.reply_text("❓ What should I disable?")

    @connection_status
    @user_admin
    async def disable_module(update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        chat = update.effective_chat
        if len(args) >= 1:
            disable_module = "MerissaRobot.Modules." + args[0].rsplit(".", 1)[0]

            try:
                module = importlib.import_module(disable_module)
            except:
                await update.effective_message.reply_text(
                    "❌ Does that module even exist?"
                )
                return

            try:
                command_list = module.__command_list__
            except:
                await update.effective_message.reply_text(
                    "❌ Module does not contain command list!",
                )
                return

            disabled_cmds = []
            failed_disabled_cmds = []

            for disable_cmd in command_list:
                if disable_cmd.startswith(CMD_STARTERS):
                    disable_cmd = disable_cmd[1:]

                if disable_cmd in set(DISABLE_CMDS + DISABLE_OTHER):
                    sql.disable_command(chat.id, str(disable_cmd).lower())
                    disabled_cmds.append(disable_cmd)
                else:
                    failed_disabled_cmds.append(disable_cmd)

            if disabled_cmds:
                disabled_cmds_string = ", ".join(disabled_cmds)
                await update.effective_message.reply_text(
                    f"✅ **Disabled** the uses of `{disabled_cmds_string}`",
                    parse_mode=ParseMode.MARKDOWN,
                )

            if failed_disabled_cmds:
                failed_disabled_cmds_string = ", ".join(failed_disabled_cmds)
                await update.effective_message.reply_text(
                    f"❌ Commands `{failed_disabled_cmds_string}` can't be disabled",
                    parse_mode=ParseMode.MARKDOWN,
                )

        else:
            await update.effective_message.reply_text("❓ What should I disable?")

    @connection_status
    @user_admin
    async def enable(update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        chat = update.effective_chat
        if len(args) >= 1:
            enable_cmd = args[0]
            if enable_cmd.startswith(CMD_STARTERS):
                enable_cmd = enable_cmd[1:]

            if sql.enable_command(chat.id, enable_cmd):
                await update.effective_message.reply_text(
                    f"✅ **Enabled** the use of `{enable_cmd}`",
                    parse_mode=ParseMode.MARKDOWN,
                )
            else:
                await update.effective_message.reply_text(
                    "❓ Is that even disabled?"
                )

        else:
            await update.effective_message.reply_text("❓ What should I enable?")

    @connection_status
    @user_admin
    async def enable_module(update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        chat = update.effective_chat

        if len(args) >= 1:
            enable_module = "MerissaRobot.Modules." + args[0].rsplit(".", 1)[0]

            try:
                module = importlib.import_module(enable_module)
            except:
                await update.effective_message.reply_text(
                    "❌ Does that module even exist?"
                )
                return

            try:
                command_list = module.__command_list__
            except:
                await update.effective_message.reply_text(
                    "❌ Module does not contain command list!",
                )
                return

            enabled_cmds = []
            failed_enabled_cmds = []

            for enable_cmd in command_list:
                if enable_cmd.startswith(CMD_STARTERS):
                    enable_cmd = enable_cmd[1:]

                if sql.enable_command(chat.id, enable_cmd):
                    enabled_cmds.append(enable_cmd)
                else:
                    failed_enabled_cmds.append(enable_cmd)

            if enabled_cmds:
                enabled_cmds_string = ", ".join(enabled_cmds)
                await update.effective_message.reply_text(
                    f"✅ **Enabled** the uses of `{enabled_cmds_string}`",
                    parse_mode=ParseMode.MARKDOWN,
                )

            if failed_enabled_cmds:
                failed_enabled_cmds_string = ", ".join(failed_enabled_cmds)
                await update.effective_message.reply_text(
                    f"❓ Are the commands `{failed_enabled_cmds_string}` even disabled?",
                    parse_mode=ParseMode.MARKDOWN,
                )

        else:
            await update.effective_message.reply_text("❓ What should I enable?")

    @connection_status
    @user_admin
    async def list_cmds(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if DISABLE_CMDS + DISABLE_OTHER:
            result = ""
            for cmd in set(DISABLE_CMDS + DISABLE_OTHER):
                result += f" • `{escape_markdown(cmd)}`\n"
            await update.effective_message.reply_text(
                f"🔧 **The following commands are toggleable:**\n{result}",
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            await update.effective_message.reply_text(
                "❌ No commands can be disabled."
            )

    # do not async - utility function
    def build_curr_disabled(chat_id: Union[str, int]) -> str:
        disabled = sql.get_all_disabled(chat_id)
        if not disabled:
            return "✅ **No commands are disabled!**"

        result = ""
        for cmd in disabled:
            result += f" • `{escape_markdown(cmd)}`\n"
        return f"⛔️ **The following commands are currently restricted:**\n{result}"

    @connection_status
    async def commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat = update.effective_chat
        await update.effective_message.reply_text(
            build_curr_disabled(chat.id),
            parse_mode=ParseMode.MARKDOWN,
        )

    def __stats__():
        return f"× {sql.num_disabled()} disabled items, across {sql.num_chats()} chats."

    def __migrate__(old_chat_id, new_chat_id):
        sql.migrate_chat(old_chat_id, new_chat_id)

    def __chat_settings__(chat_id, user_id):
        return build_curr_disabled(chat_id)

    __help__ = """
*Command Management - Enable/Disable Features*

**Check Status:**
❂ `/cmds` - Check current status of disabled commands

**Admin Commands:**
❂ `/enable <cmd>` - Enable a specific command
❂ `/disable <cmd>` - Disable a specific command
❂ `/enablemodule <module>` - Enable all commands in a module
❂ `/disablemodule <module>` - Disable all commands in a module
❂ `/listcmds` - List all commands that can be toggled

**Features:**
• Disabled commands won't work for regular users
• Admin commands can still be used by admins even when disabled
• Module-based enabling/disabling affects all commands in that module
• Connection support - manage commands in connected chats

**Example Usage:**
`/disable fun` - Disables the fun command
`/disablemodule games` - Disables all gaming commands
`/enable welcome` - Re-enables welcome messages

*Note:* Some critical commands cannot be disabled for security reasons.
"""

    DISABLE_HANDLER = CommandHandler("disable", disable)
    DISABLE_MODULE_HANDLER = CommandHandler("disablemodule", disable_module)
    ENABLE_HANDLER = CommandHandler("enable", enable)
    ENABLE_MODULE_HANDLER = CommandHandler("enablemodule", enable_module)
    COMMANDS_HANDLER = CommandHandler(["cmds", "disabled"], commands)
    TOGGLE_HANDLER = CommandHandler("listcmds", list_cmds)

    application.add_handler(DISABLE_HANDLER)
    application.add_handler(DISABLE_MODULE_HANDLER)
    application.add_handler(ENABLE_HANDLER)
    application.add_handler(ENABLE_MODULE_HANDLER)
    application.add_handler(COMMANDS_HANDLER)
    application.add_handler(TOGGLE_HANDLER)

    __mod_name__ = "Disabling ⛔️"

else:
    # Fallback when module is not loaded
    DisableAbleCommandHandler = CommandHandler
    DisableAbleRegexHandler = MessageHandler  # RegexHandler doesn't exist in PTB v22
    DisableAbleMessageHandler = MessageHandler
