import requests
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown

from MerissaRobot import application
from MerissaRobot.Modules.disable import DisableAbleCommandHandler


async def ud(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Get Urban Dictionary definition for a term.
    
    Usage: /ud <term>
    """
    message = update.effective_message
    text = message.text[len("/ud "):].strip()
    
    if not text:
        await message.reply_text(
            "Please provide a term to search for.\nUsage: `/ud <term>`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Send "typing" action to show bot is working
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        # Make API request with timeout
        response = requests.get(
            f"https://api.urbandictionary.com/v0/define?term={text}",
            timeout=10
        )
        response.raise_for_status()  # Raise an exception for bad status codes
        results = response.json()
        
        # Check if we got any results
        if not results.get("list") or len(results["list"]) == 0:
            await message.reply_text("No results found for that term.")
            return
        
        # Get the first (most popular) definition
        definition_data = results["list"][0]
        term = definition_data.get("word", text)
        definition = definition_data.get("definition", "No definition available.")
        example = definition_data.get("example", "No example available.")
        
        # Clean up the text - Urban Dictionary uses [brackets] for links
        definition = definition.replace("[", "").replace("]", "")
        example = example.replace("[", "").replace("]", "")
        
        # Truncate if too long (Telegram message limit)
        max_definition_length = 1000
        max_example_length = 500
        
        if len(definition) > max_definition_length:
            definition = definition[:max_definition_length] + "..."
            
        if len(example) > max_example_length:
            example = example[:max_example_length] + "..."
        
        # Escape markdown characters for safety
        term_escaped = escape_markdown(term, version=2)
        definition_escaped = escape_markdown(definition, version=2)
        example_escaped = escape_markdown(example, version=2)
        
        # Format the reply
        reply_text = f"*{term_escaped}*\n\n{definition_escaped}"
        
        if example.strip() and example != "No example available.":
            reply_text += f"\n\n*Example:*\n_{example_escaped}_"
        
        # Add attribution
        reply_text += f"\n\n_Definition from Urban Dictionary_"
        
        await message.reply_text(
            reply_text, 
            parse_mode=ParseMode.MARKDOWN_V2,
            disable_web_page_preview=True
        )
        
    except requests.exceptions.Timeout:
        await message.reply_text("Request timed out. Please try again later.")
    except requests.exceptions.RequestException as e:
        await message.reply_text("Error connecting to Urban Dictionary. Please try again later.")
    except (KeyError, IndexError, ValueError) as e:
        await message.reply_text("Error parsing the response. Please try again.")
    except Exception as e:
        await message.reply_text("An unexpected error occurred. Please try again later.")


# Alternative version using HTML parsing for better compatibility
async def ud_html(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Alternative Urban Dictionary function using HTML parsing.
    Can be used as a backup if the main function has issues.
    """
    message = update.effective_message
    text = message.text[len("/ud "):].strip()
    
    if not text:
        await message.reply_text(
            "Please provide a term to search for.\nUsage: <code>/ud &lt;term&gt;</code>",
            parse_mode=ParseMode.HTML
        )
        return
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        response = requests.get(
            f"https://api.urbandictionary.com/v0/define?term={text}",
            timeout=10
        )
        response.raise_for_status()
        results = response.json()
        
        if not results.get("list") or len(results["list"]) == 0:
            await message.reply_text("No results found for that term.")
            return
        
        definition_data = results["list"][0]
        term = definition_data.get("word", text)
        definition = definition_data.get("definition", "No definition available.")
        example = definition_data.get("example", "No example available.")
        
        # Clean up the text
        import html
        definition = definition.replace("[", "").replace("]", "")
        example = example.replace("[", "").replace("]", "")
        
        # Truncate if too long
        if len(definition) > 1000:
            definition = definition[:1000] + "..."
        if len(example) > 500:
            example = example[:500] + "..."
        
        # Escape HTML characters
        term_escaped = html.escape(term)
        definition_escaped = html.escape(definition)
        example_escaped = html.escape(example)
        
        reply_text = f"<b>{term_escaped}</b>\n\n{definition_escaped}"
        
        if example.strip() and example != "No example available.":
            reply_text += f"\n\n<b>Example:</b>\n<i>{example_escaped}</i>"
        
        reply_text += f"\n\n<i>Definition from Urban Dictionary</i>"
        
        await message.reply_text(
            reply_text, 
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True
        )
        
    except Exception:
        await message.reply_text("An error occurred while fetching the definition.")


# Handler registration
UD_HANDLER = DisableAbleCommandHandler(["ud"], ud)

# Add handler to application
application.add_handler(UD_HANDLER)

__command_list__ = ["ud"]
__handlers__ = [UD_HANDLER]

__help__ = """
*Urban Dictionary:*
❂ /ud <term>*:* Get the definition of a term from Urban Dictionary

*Example:*
❂ /ud python
❂ /ud machine learning

*Note:* Urban Dictionary contains user-generated content that may be inappropriate or offensive.
"""
