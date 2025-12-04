from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from pathlib import Path
import uuid

from services.gemini_client import GeminiClient
from services.vera_client import VeraClient
from config.settings import settings
from utils.logger import logger
from utils.formatters import format_fact_check_response, format_error_message, format_processing_message
from utils.validators import validate_file_size

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    
    logger.info(f"Image reçue de {user_id}")
    
    processing_msg = await update.message.reply_text(
        format_processing_message("image"),
        parse_mode=ParseMode.MARKDOWN
    )
    
    try:
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        
        file_path = settings.temp_download_path / f"{uuid.uuid4()}.jpg"
        await file.download_to_drive(file_path)
        
        try:
            validate_file_size(file_path, settings.max_image_size_mb)
        except Exception as e:
            file_path.unlink(missing_ok=True)
            await processing_msg.edit_text(
                format_error_message("file_too_large", str(e)),
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        gemini_client = GeminiClient()
        vera_client = VeraClient()
        
        analyzed = gemini_client.analyze_image(file_path, user_id)
        
        file_path.unlink(missing_ok=True)
        
        if not analyzed.claims or len(analyzed.claims) == 0:
            await processing_msg.edit_text(
                format_error_message("no_claims", "Aucune affirmation factuelle détectée dans l'image."),
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
            content_type="image",
            claims=analyzed.claims
        )
        
        await processing_msg.edit_text(
            final_response,
            parse_mode=ParseMode.MARKDOWN
        )
        
        logger.info(f"Analyse image terminée pour {user_id}")
    
    except Exception as e:
        logger.error(f"Erreur dans handle_image: {e}")
        if file_path.exists():
            file_path.unlink(missing_ok=True)
        await processing_msg.edit_text(
            format_error_message("processing_error", str(e)),
            parse_mode=ParseMode.MARKDOWN
        )