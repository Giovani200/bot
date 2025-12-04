from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from services.gemini_client import GeminiClient
from services.vera_client import VeraClient
from utils.logger import logger
from utils.formatters import format_fact_check_response, format_error_message, format_processing_message
from utils.validators import extract_urls

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text
    
    logger.info(f"Message texte reçu de {user_id}: {text[:50]}...")
    
    urls = extract_urls(text)
    if urls:
        from handlers.link_handler import handle_link
        return await handle_link(update, context)
    
    processing_msg = await update.message.reply_text(
        format_processing_message("texte"),
        parse_mode=ParseMode.MARKDOWN
    )
    
    try:
        gemini_client = GeminiClient()
        vera_client = VeraClient()
        
        analyzed = gemini_client.analyze_text(text, user_id)
        
        if not analyzed.claims or len(analyzed.claims) == 0:
            query = text
        else:
            query = "\n".join(analyzed.claims)
        
        vera_response = await vera_client.fact_check(query, user_id)
        
        if not vera_response.success:
            await processing_msg.edit_text(
                format_error_message("api_error", vera_response.error_message),
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        final_response = format_fact_check_response(
            content_summary=analyzed.summary,
            vera_response=vera_response.answer,
            content_type="texte",
            claims=analyzed.claims
        )
        
        await processing_msg.edit_text(
            final_response,
            parse_mode=ParseMode.MARKDOWN
        )
        
        logger.info(f"Réponse envoyée à {user_id}")
    
    except Exception as e:
        logger.error(f"Erreur dans handle_text: {e}")
        await processing_msg.edit_text(
            format_error_message("processing_error", str(e)),
            parse_mode=ParseMode.MARKDOWN
        )