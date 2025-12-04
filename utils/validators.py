import re
import mimetypes
from urllib.parse import urlparse
from pathlib import Path
from config.settings import settings

class ValidationError(Exception):
    pass

def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc]) and result.scheme in ['http', 'https']
    except Exception:
        return False

def extract_urls(text: str) -> list[str]:
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    urls = re.findall(url_pattern, text)
    return [url for url in urls if is_valid_url(url)]

def validate_file_size(file_path: Path, max_size_mb: int = None) -> bool:
    if max_size_mb is None:
        max_size_mb = settings.max_file_size_mb
    
    file_size = file_path.stat().st_size
    max_size_bytes = max_size_mb * 1024 * 1024
    
    if file_size > max_size_bytes:
        raise ValidationError(f"Fichier trop volumineux: {file_size / 1024 / 1024:.1f}MB (max: {max_size_mb}MB)")
    
    return True

def get_mime_type(file_path: Path) -> str:
    mime_type, _ = mimetypes.guess_type(str(file_path))
    
    if mime_type:
        return mime_type
    
    ext_to_mime = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
        '.mp4': 'video/mp4',
        '.avi': 'video/x-msvideo',
        '.mov': 'video/quicktime',
        '.mkv': 'video/x-matroska',
        '.ogg': 'audio/ogg',
        '.mp3': 'audio/mpeg',
    }
    
    return ext_to_mime.get(file_path.suffix.lower(), 'application/octet-stream')

def validate_media_type(file_path: Path, media_type: str) -> bool:
    mime = get_mime_type(file_path)
    
    if media_type == "image":
        return mime.startswith('image/')
    elif media_type == "video":
        return mime.startswith('video/')
    elif media_type == "audio":
        return mime.startswith('audio/')
    
    return False

def sanitize_filename(filename: str) -> str:
    return "".join(c for c in filename if c.isalnum() or c in (' ', '.', '_')).rstrip()