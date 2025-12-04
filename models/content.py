from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ContentType(Enum):
    TEXT = "texte"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    LINK = "lien"

class ClaimType(Enum):
    FACTUAL = "factual"
    OPINION = "opinion"
    RUMOR = "rumor"
    QUESTION = "question"
    MIXED = "mixed"
    UNKNOWN = "unknown"

@dataclass
class AnalyzedContent:
    content_type: ContentType
    user_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    extracted_text: Optional[str] = None
    summary: Optional[str] = None
    language: Optional[str] = None
    
    claims: List[str] = field(default_factory=list)
    claim_type: ClaimType = ClaimType.UNKNOWN
    
    context: Optional[str] = None

@dataclass
class VeraRequest:
    user_id: str
    query: str
    stream: bool = True

@dataclass
class VeraResponse:
    success: bool
    answer: str
    sources: List[str] = field(default_factory=list)
    error_message: Optional[str] = None

@dataclass
class BotResponse:
    success: bool
    message: str
    analyzed_content: Optional[AnalyzedContent] = None
    vera_response: Optional[VeraResponse] = None