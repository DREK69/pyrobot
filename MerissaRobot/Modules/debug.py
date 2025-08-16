import os
import logging
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from MerissaRobot import application, LOGGER
from MerissaRobot.Handler.ptb.chat_status import dev_plus

DEBUG_MODE = False


@dev_plus
async def debug(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global DEBUG_MODE
    args = update.effective_message.text.split(None, 1)
    message = update.effective_message
    
    if len(args) > 1:
        if args[1] in ("yes", "on"):
            DEBUG_MODE = True
            # Set logging level to DEBUG
            logging.getLogger().setLevel(logging.DEBUG)
            await message.reply_text("🐛 Debug mode is now **ON**.\nLogging level set to DEBUG.", parse_mode="MARKDOWN")
        elif args[1] in ("no", "off"):
            DEBUG_MODE = False
            # Reset logging level to INFO
            logging.getLogger().setLevel(logging.INFO)
            await message.reply_text("✅ Debug mode is now **OFF**.\nLogging level reset to INFO.", parse_mode="MARKDOWN")
        else:
            await message.reply_text("❌ Invalid argument. Use `yes/on` or `no/off`.", parse_mode="MARKDOWN")
    else:
        status = "**ON** 🐛" if DEBUG_MODE else "**OFF** ✅"
        log_level = logging.getLogger().getEffectiveLevel()
        level_name = logging.getLevelName(log_level)
        
        await message.reply_text(
            f"🔧 **Debug Status:** {status}\n"
            f"📊 **Log Level:** {level_name}\n"
            f"📅 **Checked:** {datetime.now().strftime('%H:%M:%S')}",
            parse_mode="MARKDOWN"
        )


support_chat = os.getenv("SUPPORT_CHAT")


@dev_plus
async def logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    try:
        # Check if log file exists
        if not os.path.exists("log.txt"):
            await update.effective_message.reply_text("❌ Log file not found!")
            return
            
        # Check file size
        file_size = os.path.getsize("log.txt")
        if file_size > 50 * 1024 * 1024:  # 50MB limit
            await update.effective_message.reply_text("⚠️ Log file too large! Please check server directly.")
            return
            
        # Send log file
        with open("log.txt", "rb") as f:
            await context.bot.send_document(
                document=f, 
                filename=f"merissa_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                chat_id=user.id,
                caption=f"📋 **MerissaRobot Logs**\n📊 **Size:** {file_size / 1024:.1f} KB\n📅 **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                parse_mode="MARKDOWN"
            )
            
        await update.effective_message.reply_text("✅ Log file sent to your PM!")
        
    except FileNotFoundError:
        await update.effective_message.reply_text("❌ Log file not found!")
    except Exception as e:
        LOGGER.error(f"Error sending logs: {e}")
        await update.effective_message.reply_text(f"❌ Error sending logs: {str(e)}")


@dev_plus
async def clear_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear the log file"""
    try:
        if os.path.exists("log.txt"):
            # Backup current logs before clearing
            backup_name = f"log_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            os.rename("log.txt", backup_name)
            
            # Create new empty log file
            open("log.txt", "w").close()
            
            await update.effective_message.reply_text(
                f"🗑️ **Logs cleared successfully!**\n"
                f"📁 **Backup saved as:** `{backup_name}`",
                parse_mode="MARKDOWN"
            )
            LOGGER.info("Log file cleared by developer")
        else:
            await update.effective_message.reply_text("❌ No log file found to clear!")
            
    except Exception as e:
        LOGGER.error(f"Error clearing logs: {e}")
        await update.effective_message.reply_text(f"❌ Error clearing logs: {str(e)}")


@dev_plus
async def system_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get system information"""
    try:
        import psutil
        import platform
        
        # System info
        system = platform.system()
        release = platform.release()
        version = platform.version()
        machine = platform.machine()
        processor = platform.processor()
        
        # Memory info
        memory = psutil.virtual_memory()
        
        # CPU info
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Disk info
        disk = psutil.disk_usage('/')
        
        info_text = f"""
🖥️ **System Information**

**OS:** {system} {release}
**Version:** {version}
**Architecture:** {machine}
**Processor:** {processor}

💾 **Memory Usage**
**Total:** {memory.total / (1024**3):.1f} GB
**Used:** {memory.used / (1024**3):.1f} GB ({memory.percent}%)
**Available:** {memory.available / (1024**3):.1f} GB

🔥 **CPU Usage**
**Cores:** {cpu_count}
**Usage:** {cpu_percent}%

💿 **Disk Usage**
**Total:** {disk.total / (1024**3):.1f} GB
**Used:** {disk.used / (1024**3):.1f} GB ({(disk.used/disk.total)*100:.1f}%)
**Free:** {disk.free / (1024**3):.1f} GB

🐛 **Debug Mode:** {'ON' if DEBUG_MODE else 'OFF'}
        """
        
        await update.effective_message.reply_text(info_text, parse_mode="MARKDOWN")
        
    except ImportError:
        await update.effective_message.reply_text("❌ psutil not installed. Install with: `pip install psutil`", parse_mode="MARKDOWN")
    except Exception as e:
        await update.effective_message.reply_text(f"❌ Error getting system info: {str(e)}")


def get_debug_status():
    """Get current debug status - can be imported by other modules"""
    return DEBUG_MODE


LOG_HANDLER = CommandHandler("logs", logs)
DEBUG_HANDLER = CommandHandler("debug", debug)
CLEAR_LOGS_HANDLER = CommandHandler("clearlogs", clear_logs)
SYSTEM_INFO_HANDLER = CommandHandler("sysinfo", system_info)

application.add_handler(LOG_HANDLER)
application.add_handler(DEBUG_HANDLER)
application.add_handler(CLEAR_LOGS_HANDLER)
application.add_handler(SYSTEM_INFO_HANDLER)

__mod_name__ = "Debug"
__help__ = """
*Debug Module - Developer Tools*

*Commands available for developers:*

❂ `/debug [on/off]` - Toggle debug mode and logging level
❂ `/logs` - Get current log file via PM
❂ `/clearlogs` - Clear log file (creates backup)
❂ `/sysinfo` - Get system information and resource usage

*Debug Features:*
• When debug mode is ON, logging level is set to DEBUG
• Log files are automatically timestamped when sent
• System automatically creates backups before clearing logs
• File size limits prevent sending oversized logs

*Note:* All commands require developer privileges.
"""

__command_list__ = ["debug", "logs", "clearlogs", "sysinfo"]
__handlers__ = [DEBUG_HANDLER, LOG_HANDLER, CLEAR_LOGS_HANDLER, SYSTEM_INFO_HANDLER]
