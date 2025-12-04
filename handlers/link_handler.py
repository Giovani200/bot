from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from services.gemini_client import GeminiClient
from services.vera_client import VeraClient
from utils.logger import logger
from utils.formatters import format_fact_check_response, format_error_message, format_processing_message
from utils.validators import extract_urls, is_valid_url

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text
    
    urls = extract_urls(text)
    
    if not urls:
        await update.message.reply_text(
            format_error_message("invalid_url", "Aucun lien valide détecté."),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    url = urls[0]
    logger.info(f"Lien reçu de {user_id}: {url}")
    
    processing_msg = await update.message.reply_text(
        format_processing_message("lien"),
        parse_mode=ParseMode.MARKDOWN
    )
    
    try:
        gemini_client = GeminiClient()
        vera_client = VeraClient()
        
        analyzed = gemini_client.analyze_url(url, user_id)
        
        if not analyzed.claims or len(analyzed.claims) == 0:
            await processing_msg.edit_text(
                format_error_message("no_claims", "Impossible d'extraire des affirmations de ce lien."),
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
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
            content_type="lien",
            claims=analyzed.claims
        )
        
        await processing_msg.edit_text(
            final_response,
            parse_mode=ParseMode.MARKDOWN
        )
        
        logger.info(f"Analyse lien terminée pour {user_id}")
    
    except Exception as e:
        logger.error(f"Erreur dans handle_link: {e}")
        await processing_msg.edit_text(
            format_error_message("processing_error", str(e)),
            parse_mode=ParseMode.MARKDOWN
        )