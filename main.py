import logging
import secrets
import string
import os
import sys
import asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# 1. Setup Logging & Output Buffering for Render
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Retrieve token from Render environment variables
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Define the persistent custom keyboard layout
REPLY_KEYBOARD = [
    ['🔤 UPPERCASE', '🔡 lowercase'],
    ['📊 Text Stats', '🔐 Generate Password'],
    ['ℹ️ Help']
]
markup = ReplyKeyboardMarkup(REPLY_KEYBOARD, resize_keyboard=True)

# 2. Command Handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command."""
    user = update.effective_user.first_name
    welcome_text = (
        f"Hi {user}! 👋 Welcome to the **Toolbox Utility Bot**.\n\n"
        "I am an all-in-one text processing utility that runs completely offline.\n"
        "Select an option from the menu below, or simply type/paste any text to process it!"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /help command and 'Help' button."""
    help_text = (
        "💡 **How to use this bot:**\n\n"
        "1. **Direct Utilities:**\n"
        "   • Press `🔐 Generate Password` to instantly get a secure, random password.\n\n"
        "2. **Text Processing:**\n"
        "   • Send me any phrase or paragraph.\n"
        "   • Select `🔤 UPPERCASE`, `🔡 lowercase`, or `📊 Text Stats` to apply the tool directly to the last thing you typed!"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown", reply_markup=markup)

# 3. Core Text Processing Functions
def generate_secure_password(length=16) -> str:
    """Generates a secure, cryptographically-safe password."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(secrets.choice(alphabet) for _ in range(length))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processes incoming text or button presses."""
    text = update.message.text
    user_data = context.user_data

    # Match system buttons first
    if text == '🔐 Generate Password':
        pwd = generate_secure_password()
        await update.message.reply_text(f"🔑 **Your Secure Password:**\n`{pwd}`", parse_mode="Markdown")
        return
        
    elif text == 'ℹ️ Help':
        await help_command(update, context)
        return

    elif text == '🔤 UPPERCASE':
        last_text = user_data.get('last_text')
        if last_text:
            await update.message.reply_text(f"Output:\n\n{last_text.upper()}")
        else:
            await update.message.reply_text("⚠️ Please send some text to me first!")
        return

    elif text == '🔡 lowercase':
        last_text = user_data.get('last_text')
        if last_text:
            await update.message.reply_text(f"Output:\n\n{last_text.lower()}")
        else:
            await update.message.reply_text("⚠️ Please send some text to me first!")
        return

    elif text == '📊 Text Stats':
        last_text = user_data.get('last_text')
        if last_text:
            char_count = len(last_text)
            word_count = len(last_text.split())
            stats = (
                f"📊 **Text Analytics:**\n"
                f"• Total Characters: `{char_count}`\n"
                f"• Total Words: `{word_count}`"
            )
            await update.message.reply_text(stats, parse_mode="Markdown")
        else:
            await update.message.reply_text("⚠️ Please send some text to me first!")
        return

    # If it's not a button command, store the text for processing
    user_data['last_text'] = text
    await update.message.reply_text(
        "📝 *Text Received!*\nChoose an action below (`🔤 UPPERCASE`, `🔡 lowercase`, or `📊 Text Stats`) to apply it to your text.",
        parse_mode="Markdown"
    )

# 4. Main Async Execution
async def main():
    logger.info("🤖 Starting Toolbox Utility Bot...")
    
    if not TOKEN:
        logger.critical("❌ DEPLOYMENT FAILED: TELEGRAM_BOT_TOKEN environment variable is missing!")
        sys.exit(1)

    # Build application
    application = Application.builder().token(TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Explicitly initialize, start, and block the application via the framework's async runner
    logger.info("🚀 Bot initialization complete. Active and polling Telegram servers...")
    
    async with application:
        await application.initialize()
        await application.start()
        await application.updater.start_polling(drop_pending_updates=True)
        
        # Keep running until standard termination
        while True:
            await asyncio.sleep(3600)

if __name__ == '__main__':
    try:
        # Securely launch loop initialization for Python 3.14 compatibility
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("👋 Bot stopped successfully.")
