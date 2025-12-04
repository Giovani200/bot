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

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    
    logger.info(f"Audio reçu de {user_id}")
    
    processing_msg = await update.message.reply_text(
        format_processing_message("audio"),
        parse_mode=ParseMode.MARKDOWN
    )
    
    file_path = None
    
    try:
        if update.message.voice:
            audio = update.message.voice
            file_extension = "ogg"
        elif update.message.audio:
            audio = update.message.audio
            file_extension = "mp3"
        else:
            await processing_msg.edit_text(
                format_error_message("unsupported_format"),
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        file = await context.bot.get_file(audio.file_id)
        
        file_path = settings.temp_download_path / f"{uuid.uuid4()}.{file_extension}"
        await file.download_to_drive(file_path)
        
        try:
            validate_file_size(file_path, settings.max_audio_size_mb)
        except Exception as e:
            file_path.unlink(missing_ok=True)
            await processing_msg.edit_text(
                format_error_message("file_too_large", str(e)),
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        gemini_client = GeminiClient()
        vera_client = VeraClient()
        
        analyzed = gemini_client.analyze_audio(file_path, user_id)
        
        file_path.unlink(missing_ok=True)
        
        if not analyzed.claims or len(analyzed.claims) == 0:
            if analyzed.extracted_text:
                query = analyzed.extracted_text
            else:
                await processing_msg.edit_text(
                    format_error_message("no_content", "Aucun contenu détecté dans l'audio."),
                    parse_mode=ParseMode.MARKDOWN
                )
                return
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
            content_type="audio",
            claims=analyzed.claims
        )
        
        await processing_msg.edit_text(
            final_response,
            parse_mode=ParseMode.MARKDOWN
        )
        
        logger.info(f"Analyse audio terminée pour {user_id}")
    
    except Exception as e:
        logger.error(f"Erreur dans handle_audio: {e}")
        if file_path and file_path.exists():
            file_path.unlink(missing_ok=True)
        await processing_msg.edit_text(
            format_error_message("processing_error", str(e)),
            parse_mode=ParseMode.MARKDOWN
        )