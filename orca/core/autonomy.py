"""
Autonomous decision-making engine for Orca OS AI agents.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

from ..core.models import CommandSuggestion, CommandAction, CommandRisk
from ..database.session import DatabaseSession
from ..database.models import AutonomousAction, User

logger = logging.getLogger(__name__)


class AutonomyLevel(str, Enum):
    """Autonomy levels for AI agents."""
    MANUAL = "manual"  # Always ask user
    ASSISTED = "assisted"  # Suggest, user confirms
    SEMI_AUTONOMOUS = "semi_autonomous"  # Auto for safe actions
    FULLY_AUTONOMOUS = "fully_autonomous"  # Auto for all actions


class AutonomousDecisionEngine:
    """Engine for making autonomous decisions."""
    
    def __init__(self, db_session: DatabaseSession):
        """Initialize autonomy engine."""
        self.db = db_session
        self.autonomy_levels = {
            'process-manager': AutonomyLevel.SEMI_AUTONOMOUS,
            'scheduler': AutonomyLevel.SEMI_AUTONOMOUS,
            'optimizer': AutonomyLevel.ASSISTED,
            'predictor': AutonomyLevel.ASSISTED,
        }
    
    def can_act_autonomously(
        self,
        agent_name: str,
        action_type: str,
        suggestion: CommandSuggestion,
        user_id: str = "default"
    ) -> bool:
        """Determine if agent can act autonomously."""
        # Get user autonomy preference
        with self.db.session() as session:
            user = session.query(User).filter_by(user_id=user_id).first()
            user_autonomous = user.autonomous_mode if user else False
        
        # Get agent autonomy level
        agent_level = self.autonomy_levels.get(agent_name, AutonomyLevel.MANUAL)
        
        # Decision logic
        if agent_level == AutonomyLevel.MANUAL:
            return False
        
        if agent_level == AutonomyLevel.ASSISTED:
            return False  # Always ask
        
        if agent_level == AutonomyLevel.SEMI_AUTONOMOUS:
            # Auto for safe actions only
            if suggestion.risk_level in [CommandRisk.SAFE, CommandRisk.MODERATE]:
                if suggestion.confidence >= 0.85:
                    return True
            return False
        
        if agent_level == AutonomyLevel.FULLY_AUTONOMOUS:
            # Auto for all actions (if user enabled)
            if user_autonomous and suggestion.confidence >= 0.75:
                return True
        
        return False
    
    def make_autonomous_decision(
        self,
        agent_name: str,
        action_type: str,
        decision_reason: str,
        action_taken: str,
        confidence: float,
        user_id: str = "default",
        metadata: Optional[Dict[str, Any]] = None
    ) -> AutonomousAction:
        """Record an autonomous decision."""
        with self.db.session() as session:
            action = AutonomousAction(
                action_type=action_type,
                agent_name=agent_name,
                decision_reason=decision_reason,
                action_taken=action_taken,
                confidence=confidence,
                user_approved=False,
                action_metadata=metadata or {}
            )
            session.add(action)
            session.commit()
            session.refresh(action)
            return action
    
    def log_autonomous_result(
        self,
        action_id: int,
        success: bool,
        user_approved: bool = False
    ):
        """Log result of autonomous action."""
        with self.db.session() as session:
            action = session.query(AutonomousAction).filter_by(id=action_id).first()
            if action:
                action.success = success
                action.user_approved = user_approved
                session.commit()

