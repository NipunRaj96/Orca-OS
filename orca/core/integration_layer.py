"""
Integration layer that connects all new features together.
"""

import logging
from typing import Dict, Any, Optional

from ..database.session import DatabaseSession
from ..core.autonomy import AutonomousDecisionEngine
from ..core.learning import PatternLearner
from ..llm.multilang import MultiLanguageManager
from ..ui.voice import VoiceInterface
from ..integration.app_bridge import AppBridge, AppIntegrationManager
from ..marketplace.marketplace import MarketplaceManager
from ..llm.manager import LLMManager

logger = logging.getLogger(__name__)


class OrcaIntegrationLayer:
    """Main integration layer for all Orca OS features."""
    
    def __init__(self, config: Any):
        """Initialize integration layer."""
        self.config = config
        self.db = DatabaseSession()
        
        # Initialize all components
        self.autonomy_engine = AutonomousDecisionEngine(self.db)
        self.pattern_learner = PatternLearner(self.db)
        self.llm_manager = LLMManager(config.llm.dict())
        self.multilang_manager = MultiLanguageManager(self.db, self.llm_manager)
        self.voice_interface = VoiceInterface()
        self.app_bridge = AppBridge(self.db, self.llm_manager)
        self.app_manager = AppIntegrationManager(self.db)
        self.marketplace_manager = MarketplaceManager(self.db)
        
        logger.info("Orca Integration Layer initialized")
    
    async def process_query_with_all_features(
        self,
        query: str,
        user_id: str = "default",
        use_voice: bool = False,
        app_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process query with all integrated features."""
        # 1. Voice input (if enabled)
        if use_voice and self.voice_interface.available:
            query = await self.voice_interface.listen_async() or query
        
        # 2. Language detection and multi-language support
        detected_lang = self.multilang_manager.detect_and_set_language(user_id, query)
        
        # 3. Get learned patterns
        patterns = self.pattern_learner.get_suggestions(user_id, query)
        
        # 4. Get app context (if app specified)
        app_context_data = None
        if app_context:
            app_context_data = self.app_bridge.get_app_context(app_context)
        
        # 5. Generate suggestion with all context
        from ..core.models import UserQuery, SystemContext
        user_query = UserQuery(query=query, user_id=user_id)
        system_context = SystemContext()
        
        # Add patterns and app context
        if patterns:
            if not hasattr(system_context, 'context'):
                system_context.context = {}
            system_context.context['learned_patterns'] = patterns
        if app_context_data:
            if not hasattr(system_context, 'context'):
                system_context.context = {}
            system_context.context.update(app_context_data)
        
        suggestion = await self.multilang_manager.generate_suggestion(
            user_query, system_context, user_id
        )
        
        # 6. Check if can act autonomously
        can_auto = self.autonomy_engine.can_act_autonomously(
            'orca-cli',
            'execute',
            suggestion,
            user_id
        )
        
        # 7. Learn from this interaction (will be called after execution)
        # self.pattern_learner.learn_from_query(...) - called after execution
        
        result = {
            'suggestion': suggestion.dict() if hasattr(suggestion, 'dict') else str(suggestion),
            'language': detected_lang,
            'patterns_used': patterns,
            'can_act_autonomously': can_auto,
            'app_context': app_context_data
        }
        
        # 8. Voice output (if enabled)
        if use_voice and self.voice_interface.available and hasattr(suggestion, 'explanation'):
            await self.voice_interface.speak_async(suggestion.explanation)
        
        return result
    
    def learn_from_execution(
        self,
        user_id: str,
        query: str,
        command: str,
        success: bool,
        context: Dict[str, Any]
    ):
        """Learn from executed command."""
        self.pattern_learner.learn_from_query(
            user_id, query, command, context, success
        )

