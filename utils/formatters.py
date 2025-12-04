from typing import Optional

def format_fact_check_response(
    content_summary: str,
    vera_response: str,
    content_type: str = "texte",
    claims: Optional[list[str]] = None
) -> str:
    type_emojis = {
        "texte": "📝",
        "image": "🖼️",
        "video": "🎬",
        "audio": "🎵",
        "lien": "🔗"
    }
    
    emoji = type_emojis.get(content_type.lower(), "📄")
    
    response_parts = [
        f"{emoji} *Analyse de {content_type}*\n",
        f"━━━━━━━━━━━━━━━━━━━━\n"
    ]
    
    if content_summary:
        response_parts.append(f"📋 *Contenu analysé :*\n{content_summary}\n\n")
    
    if claims and len(claims) > 0:
        response_parts.append(f"🎯 *Affirmations détectées :*\n")
        for i, claim in enumerate(claims[:3], 1):
            response_parts.append(f"{i}. _{claim}_\n")
        response_parts.append("\n")
    
    response_parts.append(f"🔍 *Vérification factuelle :*\n{vera_response}\n")
    response_parts.append("\n━━━━━━━━━━━━━━━━━━━━")
    response_parts.append("\n💡 _Envoyez-moi du contenu à vérifier !_")
    
    return "".join(response_parts)

def format_error_message(error_type: str, details: Optional[str] = None) -> str:
    errors = {
        "processing_error": "❌ *Erreur de traitement*",
        "file_too_large": "⚠️ *Fichier trop volumineux*",
        "invalid_url": "🔗 *URL invalide*",
        "no_content": "📭 *Aucun contenu détecté*",
        "no_claims": "🤷 *Aucune affirmation à vérifier*",
        "api_error": "🔌 *Erreur API*",
        "unsupported_format": "❌ *Format non supporté*"
    }
    
    message = errors.get(error_type, "❌ *Erreur inconnue*")
    
    if details:
        message += f"\n\n{details}"
    
    message += "\n\n💡 _Réessayez ou envoyez /help pour plus d'infos._"
    
    return message

def format_processing_message(content_type: str) -> str:
    return f"⏳ *Analyse en cours...*\n\n🔄 Traitement du {content_type}..."

def truncate_text(text: str, max_length: int = 4000) -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."

def escape_markdown(text: str) -> str:
    escape_chars = '_*[]()~`>#+-=|{}.!'
    return ''.join('\\' + char if char in escape_chars else char for char in text)