from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

from config.settings import settings
from handlers import handle_text, handle_image, handle_video, handle_audio
from utils.logger import logger

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = """
🤖 *Bot de Fact-Checking Vera*

Bienvenue ! Je vérifie la véracité des informations.

📝 *Ce que je peux analyser :*
• Textes et questions
• Images avec texte
• Vidéos
• Messages vocaux
• Liens (articles, YouTube, etc.)

💡 *Comment m'utiliser :*
Envoyez-moi simplement du contenu et j'analyserai les affirmations factuelles.

    """
    await update.message.reply_text(welcome_message, parse_mode="Markdown")
    logger.info(f"Commande /start de {update.effective_user.id}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📚 *Aide - Bot Fact-Checking*

*Types de contenu acceptés :*
✅ Texte simple
✅ Images (PNG, JPG, GIF, WebP)
✅ Vidéos (MP4, AVI, MOV, MKV)
✅ Audio et messages vocaux
✅ Liens web et YouTube

*Limites de taille :*
• Images : 10 MB
• Vidéos : 50 MB
• Audio : 10 MB

*Commandes :*
/start - Démarrer le bot
/help - Afficher cette aide

*Support :* contact@example.com
    """
    await update.message.reply_text(help_text, parse_mode="Markdown")
    logger.info(f"Commande /help de {update.effective_user.id}")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Exception: {context.error}", exc_info=context.error)
    
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "❌ Une erreur s'est produite. Veuillez réessayer.",
            parse_mode="Markdown"
        )

def main():
    logger.info("Démarrage du bot Telegram Fact-Checker...")
    
    application = Application.builder().token(settings.telegram_bot_token).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    application.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, handle_audio))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    application.add_error_handler(error_handler)
    
    logger.info("Bot démarré avec succès ! En attente de messages...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()