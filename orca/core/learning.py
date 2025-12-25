"""
Pattern learning system for Orca OS.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict, Counter

from ..database.session import DatabaseSession
from ..database.models import Pattern, Query, Result, User

logger = logging.getLogger(__name__)


class PatternLearner:
    """Learns patterns from user behavior."""
    
    def __init__(self, db_session: DatabaseSession):
        """Initialize pattern learner."""
        self.db = db_session
    
    def learn_from_query(
        self,
        user_id: str,
        query_text: str,
        command: str,
        context: Dict[str, Any],
        success: bool
    ):
        """Learn patterns from a user query."""
        # Learn command patterns
        self._learn_command_pattern(user_id, query_text, command, success)
        
        # Learn time patterns
        self._learn_time_pattern(user_id, query_text, datetime.now())
        
        # Learn context patterns
        self._learn_context_pattern(user_id, query_text, context)
    
    def _learn_command_pattern(
        self,
        user_id: str,
        query_text: str,
        command: str,
        success: bool
    ):
        """Learn command-to-query patterns."""
        with self.db.session() as session:
            # Check if pattern exists
            # Query command patterns (simplified - check all and filter in Python)
            all_command_patterns = session.query(Pattern).filter_by(
                user_id=user_id,
                pattern_type='command'
            ).all()
            existing = None
            for p in all_command_patterns:
                if p.pattern_data.get('query') == query_text.lower():
                    existing = p
                    break
            
            if existing:
                # Update frequency and confidence
                existing.frequency += 1
                if success:
                    existing.confidence = min(1.0, existing.confidence + 0.1)
                else:
                    existing.confidence = max(0.0, existing.confidence - 0.1)
                existing.last_seen = datetime.now()
                existing.pattern_data['command'] = command
            else:
                # Create new pattern
                pattern = Pattern(
                    user_id=user_id,
                    pattern_type='command',
                    pattern_data={
                        'query': query_text.lower(),
                        'command': command,
                        'success_count': 1 if success else 0,
                        'total_count': 1
                    },
                    frequency=1,
                    confidence=1.0 if success else 0.5
                )
                session.add(pattern)
            
            session.commit()
    
    def _learn_time_pattern(
        self,
        user_id: str,
        query_text: str,
        timestamp: datetime
    ):
        """Learn time-based patterns."""
        hour = timestamp.hour
        day_of_week = timestamp.weekday()
        
        with self.db.session() as session:
            pattern_key = f"{query_text.lower()}_{hour}_{day_of_week}"
            # Query time patterns (simplified - check all and filter in Python)
            all_time_patterns = session.query(Pattern).filter_by(
                user_id=user_id,
                pattern_type='time'
            ).all()
            existing = None
            for p in all_time_patterns:
                if p.pattern_data.get('key') == pattern_key:
                    existing = p
                    break
            
            if existing:
                existing.frequency += 1
                existing.last_seen = timestamp
            else:
                pattern = Pattern(
                    user_id=user_id,
                    pattern_type='time',
                    pattern_data={
                        'key': pattern_key,
                        'query': query_text.lower(),
                        'hour': hour,
                        'day_of_week': day_of_week
                    },
                    frequency=1
                )
                session.add(pattern)
            
            session.commit()
    
    def _learn_context_pattern(
        self,
        user_id: str,
        query_text: str,
        context: Dict[str, Any]
    ):
        """Learn context-based patterns."""
        # Extract relevant context
        context_key = self._extract_context_key(context)
        
        with self.db.session() as session:
            # Query context patterns (simplified - check all and filter in Python)
            all_context_patterns = session.query(Pattern).filter_by(
                user_id=user_id,
                pattern_type='context'
            ).all()
            existing = None
            for p in all_context_patterns:
                if p.pattern_data.get('key') == context_key:
                    existing = p
                    break
            
            if existing:
                existing.frequency += 1
                existing.last_seen = datetime.now()
            else:
                pattern = Pattern(
                    user_id=user_id,
                    pattern_type='context',
                    pattern_data={
                        'key': context_key,
                        'query': query_text.lower(),
                        'context': context_key
                    },
                    frequency=1
                )
                session.add(pattern)
            
            session.commit()
    
    def _extract_context_key(self, context: Dict[str, Any]) -> str:
        """Extract key context features."""
        # Simple context key based on system state
        cpu = context.get('cpu_percent', 0)
        memory = context.get('memory_percent', 0)
        disk = context.get('disk_percent', 0)
        
        # Categorize
        cpu_level = 'high' if cpu > 80 else 'medium' if cpu > 50 else 'low'
        mem_level = 'high' if memory > 80 else 'medium' if memory > 50 else 'low'
        
        return f"{cpu_level}_{mem_level}"
    
    def get_suggestions(
        self,
        user_id: str,
        query_text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Get learned pattern suggestions."""
        suggestions = []
        
        with self.db.session() as session:
            # Command patterns
            # Get all command patterns and filter in Python
            all_patterns = session.query(Pattern).filter_by(
                user_id=user_id,
                pattern_type='command'
            ).all()
            command_patterns = [
                p for p in all_patterns
                if query_text.lower() in p.pattern_data.get('query', '').lower()
            ]
            command_patterns = sorted(command_patterns, key=lambda x: x.frequency, reverse=True)[:5]
            
            for pattern in command_patterns:
                suggestions.append({
                    'type': 'command',
                    'command': pattern.pattern_data.get('command'),
                    'confidence': pattern.confidence,
                    'frequency': pattern.frequency
                })
            
            # Time patterns (if similar time)
            if context:
                hour = datetime.now().hour
                # Get time patterns for current hour
                all_time_patterns = session.query(Pattern).filter_by(
                    user_id=user_id,
                    pattern_type='time'
                ).all()
                time_patterns = [
                    p for p in all_time_patterns
                    if p.pattern_data.get('hour') == hour
                ]
                time_patterns = sorted(time_patterns, key=lambda x: x.frequency, reverse=True)[:3]
                
                for pattern in time_patterns:
                    suggestions.append({
                        'type': 'time',
                        'query': pattern.pattern_data.get('query'),
                        'confidence': pattern.confidence,
                        'frequency': pattern.frequency
                    })
        
        return suggestions
    
    def get_user_patterns_summary(self, user_id: str) -> Dict[str, Any]:
        """Get summary of learned patterns for user."""
        with self.db.session() as session:
            patterns = session.query(Pattern).filter_by(user_id=user_id).all()
            
            summary = {
                'total_patterns': len(patterns),
                'by_type': defaultdict(int),
                'top_commands': [],
                'confidence_avg': 0.0
            }
            
            command_patterns = [p for p in patterns if p.pattern_type == 'command']
            if command_patterns:
                summary['confidence_avg'] = sum(p.confidence for p in command_patterns) / len(command_patterns)
                summary['top_commands'] = sorted(
                    command_patterns,
                    key=lambda x: x.frequency * x.confidence,
                    reverse=True
                )[:10]
            
            for pattern in patterns:
                summary['by_type'][pattern.pattern_type] += 1
            
            return summary

