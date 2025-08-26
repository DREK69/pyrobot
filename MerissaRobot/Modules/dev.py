import asyncio
import os
import subprocess
import sys
from contextlib import suppress
from time import sleep

from telegram import Update
from telegram.error import Unauthorized, TelegramError
from telegram.ext import ContextTypes, CommandHandler

import MerissaRobot
from MerissaRobot import application, LOGGER
from MerissaRobot.Handler.ptb.chat_status import dev_plus


@dev_plus
async def allow_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        state = "Lockdown is " + ("on" if not MerissaRobot.ALLOW_CHATS else "off")
        await update.effective_message.reply_text(f"🔒 **Current state:** {state}", parse_mode="MARKDOWN")
        return
        
    if args[0].lower() in ["off", "no"]:
        MerissaRobot.ALLOW_CHATS = True
        status = "**DISABLED** ✅\nBot can now join new groups."
    elif args[0].lower() in ["yes", "on"]:
        MerissaRobot.ALLOW_CHATS = False
        status = "**ENABLED** 🔒\nBot will not join new groups."
    else:
        await update.effective_message.reply_text(
            "❌ **Invalid format!**\n"
            "Usage: `/lockdown yes/on` or `/lockdown no/off`", 
            parse_mode="MARKDOWN"
        )
        return
        
    await update.effective_message.reply_text(
        f"🔒 **Lockdown {status}**", 
        parse_mode="MARKDOWN"
    )
    LOGGER.info(f"Lockdown toggled by {update.effective_user.id}: ALLOW_CHATS = {MerissaRobot.ALLOW_CHATS}")


@dev_plus
async def leave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    args = context.args
    
    if args:
        chat_id = str(args[0])
        try:
            # Get chat info first
            try:
                chat_info = await bot.get_chat(int(chat_id))
                chat_name = chat_info.title or "Unknown Chat"
            except:
                chat_name = "Unknown Chat"
                
            await bot.leave_chat(int(chat_id))
            
            with suppress(Unauthorized):
                await update.effective_message.reply_text(
                    f"✅ **Successfully left chat!**\n"
                    f"📋 **Chat:** {chat_name}\n"
                    f"🆔 **ID:** `{chat_id}`",
                    parse_mode="MARKDOWN"
                )
            LOGGER.info(f"Left chat {chat_id} ({chat_name}) by command from {update.effective_user.id}")
            
        except TelegramError as e:
            await update.effective_message.reply_text(
                f"❌ **Failed to leave chat!**\n"
                f"🆔 **Chat ID:** `{chat_id}`\n"
                f"⚠️ **Error:** {str(e)}",
                parse_mode="MARKDOWN"
            )
            LOGGER.error(f"Failed to leave chat {chat_id}: {e}")
    else:
        await update.effective_message.reply_text(
            "❌ **Missing chat ID!**\n"
            "Usage: `/leave <chat_id>`",
            parse_mode="MARKDOWN"
        )


@dev_plus
async def gitpull(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sent_msg = await update.effective_message.reply_text(
        "🔄 **Pulling changes from repository...**\n"
        "⏳ This may take a moment.",
        parse_mode="MARKDOWN"
    )
    
    try:
        # Execute git pull
        result = subprocess.run(
            ["git", "pull"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            changes = result.stdout.strip()
            if "Already up to date" in changes:
                await sent_msg.edit_text(
                    "✅ **Repository is already up to date!**\n"
                    "No restart needed.",
                    parse_mode="MARKDOWN"
                )
                return
            else:
                await sent_msg.edit_text(
                    f"✅ **Changes pulled successfully!**\n"
                    f"```\n{changes[:500]}```\n"
                    "🔄 Restarting in 5 seconds...",
                    parse_mode="MARKDOWN"
                )
        else:
            await sent_msg.edit_text(
                f"❌ **Git pull failed!**\n"
                f"```\n{result.stderr[:500]}```",
                parse_mode="MARKDOWN"
            )
            return
            
    except subprocess.TimeoutExpired:
        await sent_msg.edit_text("❌ **Git pull timed out!**", parse_mode="MARKDOWN")
        return
    except Exception as e:
        await sent_msg.edit_text(f"❌ **Error during git pull:** {str(e)}", parse_mode="MARKDOWN")
        return

    # Countdown and restart
    sent_msg_text = "🔄 **Restarting in** "
    
    for i in reversed(range(5)):
        await sent_msg.edit_text(
            sent_msg_text + f"**{i + 1}** seconds...",
            parse_mode="MARKDOWN"
        )
        await asyncio.sleep(1)

    await sent_msg.edit_text("🔄 **Restarting now...**", parse_mode="MARKDOWN")
    LOGGER.info(f"Bot restart initiated by {update.effective_user.id} via gitpull")
    
    # Restart the bot
    os.execl(sys.executable, sys.executable, *sys.argv)


@dev_plus
async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        "🔄 **Restarting bot...**\n"
        "⏳ Starting new instance and shutting down current one.",
        parse_mode="MARKDOWN"
    )
    
    LOGGER.info(f"Bot restart initiated by {update.effective_user.id}")
    
    # Small delay to ensure message is sent
    await asyncio.sleep(2)
    
    os.execl(sys.executable, sys.executable, *sys.argv)


@dev_plus
async def get_chat_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get detailed information about a chat"""
    args = context.args
    
    if not args:
        await update.effective_message.reply_text(
            "❌ **Missing chat ID!**\n"
            "Usage: `/chatinfo <chat_id>`",
            parse_mode="MARKDOWN"
        )
        return
        
    chat_id = args[0]
    try:
        chat = await context.bot.get_chat(int(chat_id))
        member_count = await chat.get_member_count()
        
        info_text = f"""
📋 **Chat Information**

**Name:** {chat.title or 'N/A'}
**ID:** `{chat.id}`
**Type:** {chat.type}
**Members:** {member_count}
**Username:** @{chat.username or 'N/A'}
**Description:** {chat.description or 'N/A'}

**Settings:**
**All Members Admin:** {getattr(chat.permissions, 'can_send_messages', 'N/A')}
**Slow Mode:** {getattr(chat, 'slow_mode_delay', 'N/A')}
"""
        
        await update.effective_message.reply_text(info_text, parse_mode="MARKDOWN")
        
    except Exception as e:
        await update.effective_message.reply_text(
            f"❌ **Error getting chat info:**\n`{str(e)}`",
            parse_mode="MARKDOWN"
        )


@dev_plus
async def system_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get system and bot statistics"""
    try:
        import psutil
        
        # CPU and Memory
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        # Bot stats (if available)
        try:
            import MerissaRobot.Database.sql.users_sql as user_sql
            total_users = user_sql.num_users()
            total_chats = user_sql.num_chats()
        except:
            total_users = "N/A"
            total_chats = "N/A"
        
        stats_text = f"""
📊 **System & Bot Statistics**

**System:**
🔥 **CPU Usage:** {cpu_percent}%
💾 **RAM Usage:** {memory.percent}%
💾 **RAM Used:** {memory.used / (1024**3):.1f} GB / {memory.total / (1024**3):.1f} GB

**Bot Stats:**
👥 **Total Users:** {total_users}
💬 **Total Chats:** {total_chats}
🔒 **Lockdown Mode:** {"ON" if not MerissaRobot.ALLOW_CHATS else "OFF"}
"""
        
        await update.effective_message.reply_text(stats_text, parse_mode="MARKDOWN")
        
    except ImportError:
        await update.effective_message.reply_text(
            "❌ **psutil not installed!**\n"
            "Install with: `pip install psutil`",
            parse_mode="MARKDOWN"
        )
    except Exception as e:
        await update.effective_message.reply_text(
            f"❌ **Error getting stats:** {str(e)}",
            parse_mode="MARKDOWN"
        )


LEAVE_HANDLER = CommandHandler("leave", leave)
GITPULL_HANDLER = CommandHandler("gitpull", gitpull)
RESTART_HANDLER = CommandHandler("reboot", restart)
ALLOWGROUPS_HANDLER = CommandHandler("lockdown", allow_groups)
CHATINFO_HANDLER = CommandHandler("chatinfo", get_chat_info)
STATS_HANDLER = CommandHandler("sysstats", system_stats)

application.add_handler(ALLOWGROUPS_HANDLER)
application.add_handler(LEAVE_HANDLER)
application.add_handler(GITPULL_HANDLER)
application.add_handler(RESTART_HANDLER)
application.add_handler(CHATINFO_HANDLER)
application.add_handler(STATS_HANDLER)

__mod_name__ = "Dev Commands"
__help__ = """
*Developer Commands - Bot Management*

*Available commands for developers:*

**Bot Control:**
❂ `/lockdown [on/off]` - Toggle bot's ability to join new groups
❂ `/leave <chat_id>` - Make bot leave a specific chat
❂ `/reboot` - Restart the bot immediately
❂ `/gitpull` - Pull latest changes from repository and restart

**Information:**
❂ `/chatinfo <chat_id>` - Get detailed information about a chat
❂ `/sysstats` - Get system and bot statistics

**Features:**
• Lockdown mode prevents bot from joining new groups
• Git pull automatically checks for updates before restarting
• Chat info shows member count, permissions, and settings
• System stats shows CPU, RAM usage and bot statistics
• All commands include proper error handling and logging

*Note:* All commands require developer privileges and are logged for security.
"""

__handlers__ = [
    LEAVE_HANDLER, 
    GITPULL_HANDLER, 
    RESTART_HANDLER, 
    ALLOWGROUPS_HANDLER,
    CHATINFO_HANDLER,
    STATS_HANDLER
]
