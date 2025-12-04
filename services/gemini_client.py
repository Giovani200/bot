import google.generativeai as genai
from pathlib import Path
from typing import Optional, List
from config.settings import settings
from utils.logger import logger
from models.content import AnalyzedContent, ContentType, ClaimType

class GeminiClient:
    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)
        logger.info(f"GeminiClient initialisé avec le modèle: {settings.gemini_model}")
    
    def analyze_text(self, text: str, user_id: str) -> AnalyzedContent:
        prompt = f"""Analyse ce texte et extrait les affirmations factuelles vérifiables.

Texte: {text}

Retourne au format:
RESUME: [résumé court du contenu]
AFFIRMATIONS:
1. [première affirmation factuelle]
2. [deuxième affirmation factuelle]
etc.

Si aucune affirmation factuelle, retourne juste le résumé."""

        try:
            response = self.model.generate_content(prompt)
            result = response.text
            
            lines = result.strip().split('\n')
            summary = ""
            claims = []
            
            in_claims = False
            for line in lines:
                if line.startswith('RESUME:'):
                    summary = line.replace('RESUME:', '').strip()
                elif line.startswith('AFFIRMATIONS:'):
                    in_claims = True
                elif in_claims and line.strip():
                    claim = line.strip()
                    if claim[0].isdigit():
                        claim = claim.split('.', 1)[1].strip() if '.' in claim else claim
                    if claim:
                        claims.append(claim)
            
            return AnalyzedContent(
                content_type=ContentType.TEXT,
                user_id=user_id,
                extracted_text=text,
                summary=summary or text[:200],
                claims=claims,
                claim_type=ClaimType.FACTUAL if claims else ClaimType.UNKNOWN
            )
        
        except Exception as e:
            logger.error(f"Erreur analyse texte Gemini: {e}")
            return AnalyzedContent(
                content_type=ContentType.TEXT,
                user_id=user_id,
                extracted_text=text,
                summary=text[:200],
                claims=[text],
                claim_type=ClaimType.UNKNOWN
            )
    
    def analyze_image(self, image_path: Path, user_id: str) -> AnalyzedContent:
        prompt = """Analyse cette image et:
1. Décris son contenu
2. Identifie toute affirmation factuelle visible (texte, graphiques, données)
3. Extrait les affirmations vérifiables

Format de réponse:
DESCRIPTION: [description de l'image]
TEXTE_EXTRAIT: [texte visible dans l'image]
AFFIRMATIONS:
1. [affirmation 1]
2. [affirmation 2]"""

        try:
            image_file = genai.upload_file(path=str(image_path))
            response = self.model.generate_content([prompt, image_file])
            result = response.text
            
            description = ""
            extracted_text = ""
            claims = []
            
            lines = result.strip().split('\n')
            in_claims = False
            
            for line in lines:
                if line.startswith('DESCRIPTION:'):
                    description = line.replace('DESCRIPTION:', '').strip()
                elif line.startswith('TEXTE_EXTRAIT:'):
                    extracted_text = line.replace('TEXTE_EXTRAIT:', '').strip()
                elif line.startswith('AFFIRMATIONS:'):
                    in_claims = True
                elif in_claims and line.strip():
                    claim = line.strip()
                    if claim[0].isdigit():
                        claim = claim.split('.', 1)[1].strip() if '.' in claim else claim
                    if claim:
                        claims.append(claim)
            
            return AnalyzedContent(
                content_type=ContentType.IMAGE,
                user_id=user_id,
                extracted_text=extracted_text,
                summary=description,
                claims=claims,
                claim_type=ClaimType.FACTUAL if claims else ClaimType.UNKNOWN
            )
        
        except Exception as e:
            logger.error(f"Erreur analyse image Gemini: {e}")
            raise
    
    def analyze_video(self, video_path: Path, user_id: str) -> AnalyzedContent:
        prompt = """Analyse cette vidéo et:
1. Résume le contenu principal
2. Identifie les affirmations factuelles
3. Extrait le texte visible ou parlé

Format:
RESUME: [résumé de la vidéo]
AFFIRMATIONS:
1. [affirmation 1]
2. [affirmation 2]"""

        try:
            video_file = genai.upload_file(path=str(video_path))
            response = self.model.generate_content([prompt, video_file])
            result = response.text
            
            summary = ""
            claims = []
            
            lines = result.strip().split('\n')
            in_claims = False
            
            for line in lines:
                if line.startswith('RESUME:'):
                    summary = line.replace('RESUME:', '').strip()
                elif line.startswith('AFFIRMATIONS:'):
                    in_claims = True
                elif in_claims and line.strip():
                    claim = line.strip()
                    if claim[0].isdigit():
                        claim = claim.split('.', 1)[1].strip() if '.' in claim else claim
                    if claim:
                        claims.append(claim)
            
            return AnalyzedContent(
                content_type=ContentType.VIDEO,
                user_id=user_id,
                summary=summary,
                claims=claims,
                claim_type=ClaimType.FACTUAL if claims else ClaimType.UNKNOWN
            )
        
        except Exception as e:
            logger.error(f"Erreur analyse vidéo Gemini: {e}")
            raise
    
    def analyze_audio(self, audio_path: Path, user_id: str) -> AnalyzedContent:
        prompt = """Transcris cet audio et:
1. Extrait le texte parlé
2. Identifie les affirmations factuelles

Format:
TRANSCRIPTION: [texte complet]
AFFIRMATIONS:
1. [affirmation 1]
2. [affirmation 2]"""

        try:
            audio_file = genai.upload_file(path=str(audio_path))
            response = self.model.generate_content([prompt, audio_file])
            result = response.text
            
            transcription = ""
            claims = []
            
            lines = result.strip().split('\n')
            in_claims = False
            
            for line in lines:
                if line.startswith('TRANSCRIPTION:'):
                    transcription = line.replace('TRANSCRIPTION:', '').strip()
                elif line.startswith('AFFIRMATIONS:'):
                    in_claims = True
                elif in_claims and line.strip():
                    claim = line.strip()
                    if claim[0].isdigit():
                        claim = claim.split('.', 1)[1].strip() if '.' in claim else claim
                    if claim:
                        claims.append(claim)
            
            return AnalyzedContent(
                content_type=ContentType.AUDIO,
                user_id=user_id,
                extracted_text=transcription,
                summary=transcription[:200],
                claims=claims,
                claim_type=ClaimType.FACTUAL if claims else ClaimType.UNKNOWN
            )
        
        except Exception as e:
            logger.error(f"Erreur analyse audio Gemini: {e}")
            raise
    
    def analyze_url(self, url: str, user_id: str) -> AnalyzedContent:
        prompt = f"""Analyse ce lien et extrait les informations principales:

URL: {url}

Indique:
1. Type de contenu (article, vidéo YouTube, etc.)
2. Sujet principal
3. Affirmations factuelles clés

Format:
TYPE: [type de contenu]
SUJET: [sujet principal]
AFFIRMATIONS:
1. [affirmation 1]
2. [affirmation 2]"""

        try:
            response = self.model.generate_content(prompt)
            result = response.text
            
            content_type_line = ""
            subject = ""
            claims = []
            
            lines = result.strip().split('\n')
            in_claims = False
            
            for line in lines:
                if line.startswith('TYPE:'):
                    content_type_line = line.replace('TYPE:', '').strip()
                elif line.startswith('SUJET:'):
                    subject = line.replace('SUJET:', '').strip()
                elif line.startswith('AFFIRMATIONS:'):
                    in_claims = True
                elif in_claims and line.strip():
                    claim = line.strip()
                    if claim[0].isdigit():
                        claim = claim.split('.', 1)[1].strip() if '.' in claim else claim
                    if claim:
                        claims.append(claim)
            
            return AnalyzedContent(
                content_type=ContentType.LINK,
                user_id=user_id,
                extracted_text=url,
                summary=f"{content_type_line} - {subject}" if content_type_line else subject,
                claims=claims,
                claim_type=ClaimType.FACTUAL if claims else ClaimType.UNKNOWN,
                context=url
            )
        
        except Exception as e:
            logger.error(f"Erreur analyse URL Gemini: {e}")
            return AnalyzedContent(
                content_type=ContentType.LINK,
                user_id=user_id,
                extracted_text=url,
                summary=f"Analyse du lien: {url}",
                claims=[f"Vérifier le contenu de {url}"],
                claim_type=ClaimType.UNKNOWN,
                context=url
            )