# 4. Main Execution
def main():
    # Force Python to flush stdout/stderr immediately so logs show up on Render
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)

    logger.info("🤖 Starting Toolbox Utility Bot...")
    
    if not TOKEN:
        logger.critical("❌ DEPLOYMENT FAILED: TELEGRAM_BOT_TOKEN environment variable is missing!")
        return

    # Build application
    application = Application.builder().token(TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start long polling mode
    logger.info("🚀 Bot initialization complete. Active and polling Telegram servers...")
    application.run_polling(drop_pending_updates=True) # Clears old text backlog on startup

if __name__ == '__main__':
    main()
