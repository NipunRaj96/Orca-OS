"""
Multi-language support for Orca OS LLM.
"""

import logging
from typing import Dict, Any, Optional, List
import re

from ..database.session import DatabaseSession
from ..database.models import User

logger = logging.getLogger(__name__)


class LanguageDetector:
    """Detects user language from query."""
    
    # Language detection patterns (simple keyword-based)
    LANGUAGE_KEYWORDS = {
        'es': ['muestra', 'mostrar', 'usar', 'disco', 'memoria', 'proceso'],
        'fr': ['afficher', 'montrer', 'utiliser', 'disque', 'mémoire', 'processus'],
        'de': ['zeigen', 'anzeigen', 'verwenden', 'festplatte', 'speicher', 'prozess'],
        'zh': ['显示', '展示', '使用', '磁盘', '内存', '进程'],
        'ja': ['表示', '表示する', '使用', 'ディスク', 'メモリ', 'プロセス'],
        'pt': ['mostrar', 'exibir', 'usar', 'disco', 'memória', 'processo'],
        'ru': ['показать', 'отобразить', 'использовать', 'диск', 'память', 'процесс'],
        'ar': ['عرض', 'إظهار', 'استخدام', 'القرص', 'الذاكرة', 'العملية'],
        'hi': ['दिखाएं', 'प्रदर्शित', 'उपयोग', 'डिस्क', 'मेमोरी', 'प्रक्रिया'],
    }
    
    def detect(self, text: str) -> str:
        """Detect language from text."""
        text_lower = text.lower()
        
        # Count matches for each language
        scores = {}
        for lang, keywords in self.LANGUAGE_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                scores[lang] = score
        
        if scores:
            return max(scores, key=scores.get)
        
        # Default to English
        return 'en'
    
    def is_english(self, text: str) -> bool:
        """Check if text is likely English."""
        # Simple heuristic: English uses ASCII characters primarily
        ascii_ratio = sum(1 for c in text if ord(c) < 128) / len(text) if text else 0
        return ascii_ratio > 0.8


class MultiLanguageManager:
    """Manages multi-language LLM interactions."""
    
    def __init__(self, db_session: DatabaseSession, base_llm_manager):
        """Initialize multi-language manager."""
        self.db = db_session
        self.llm_manager = base_llm_manager
        self.detector = LanguageDetector()
        self.language_models = {
            # Map language codes to model names
            'en': None,  # Use default
            'es': 'llama3.2-vision',  # Spanish
            'fr': 'llama3.2-vision',  # French
            'de': 'llama3.2-vision',  # German
            'zh': 'llama3.2-vision',  # Chinese
            'ja': 'llama3.2-vision',  # Japanese
            'pt': 'llama3.2-vision',  # Portuguese
            'ru': 'llama3.2-vision',  # Russian
            'ar': 'llama3.2-vision',  # Arabic
            'hi': 'llama3.2-vision',  # Hindi
        }
    
    def get_user_language(self, user_id: str = "default") -> str:
        """Get user's preferred language."""
        with self.db.session() as session:
            user = session.query(User).filter_by(user_id=user_id).first()
            return user.language if user and user.language else 'en'
    
    def set_user_language(self, user_id: str, language: str):
        """Set user's preferred language."""
        with self.db.session() as session:
            user = session.query(User).filter_by(user_id=user_id).first()
            if not user:
                user = User(user_id=user_id, language=language)
                session.add(user)
            else:
                user.language = language
            session.commit()
    
    def detect_and_set_language(self, user_id: str, query: str) -> str:
        """Detect language from query and update user preference."""
        detected = self.detector.detect(query)
        
        # Only update if not English (to avoid false positives)
        if detected != 'en':
            self.set_user_language(user_id, detected)
        
        return detected
    
    async def generate_suggestion(
        self,
        query: Any,  # Can be UserQuery or str
        context: Any,
        user_id: str = "default"
    ) -> Any:
        """Generate suggestion with language support."""
        # Extract query string for language detection
        query_str = query.query if hasattr(query, 'query') else str(query)
        
        # Get or detect language
        user_lang = self.get_user_language(user_id)
        if user_lang == 'en':
            detected_lang = self.detector.detect(query_str)
            if detected_lang != 'en':
                user_lang = detected_lang
                self.set_user_language(user_id, user_lang)
        
        # Get model for language
        model_name = self.language_models.get(user_lang)
        if model_name:
            # Temporarily switch model
            original_model = self.llm_manager.model_name
            self.llm_manager.model_name = model_name
            try:
                result = await self.llm_manager.generate_suggestion(query, context)
            finally:
                self.llm_manager.model_name = original_model
            return result
        else:
            # Use default model
            return await self.llm_manager.generate_suggestion(query, context)
    
    def translate_response(self, text: str, target_language: str) -> str:
        """Translate response text (placeholder for future implementation)."""
        # For now, return as-is
        # Future: Use LLM for translation
        return text

