"""
Failure learning system for Orca OS.
Tracks failed commands, analyzes patterns, and improves suggestions.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from sqlalchemy import func, and_

from ...database.session import DatabaseSession
from ...database.models import Query, Result, Pattern
from ...database.init_db import initialize_database

logger = logging.getLogger(__name__)


class FailureLearningSystem:
    """System for learning from command failures."""
    
    def __init__(self, user_id: str = "default"):
        """Initialize failure learning system."""
        initialize_database()
        self.db = DatabaseSession()
        self.user_id = user_id
    
    def track_failure(
        self,
        query_text: str,
        command: str,
        error: Optional[str] = None,
        exit_code: Optional[int] = None,
        context: Optional[Dict] = None
    ):
        """Track a failed command execution."""
        try:
            with self.db.session() as session:
                # Find the most recent query matching this
                query = session.query(Query)\
                    .filter_by(user_id=self.user_id)\
                    .filter(Query.query_text == query_text)\
                    .order_by(Query.timestamp.desc())\
                    .first()
                
                if query:
                    # Update or create result
                    result = session.query(Result)\
                        .filter_by(query_id=query.id)\
                        .first()
                    
                    if result:
                        result.success = False
                        result.exit_code = exit_code
                        result.stderr = error
                    else:
                        result = Result(
                            query_id=query.id,
                            command=command,
                            success=False,
                            exit_code=exit_code,
                            stderr=error
                        )
                        session.add(result)
                    
                    session.commit()
                    logger.debug(f"Tracked failure: {command[:50]}")
        except Exception as e:
            logger.error(f"Error tracking failure: {e}")
    
    def analyze_failure_patterns(self, days: int = 30) -> Dict[str, Any]:
        """Analyze patterns in failures."""
        try:
            with self.db.session() as session:
                cutoff_date = datetime.now() - timedelta(days=days)
                
                # Get all failed commands
                failed_results = session.query(Result)\
                    .join(Query)\
                    .filter(Query.user_id == self.user_id)\
                    .filter(Result.success == False)\
                    .filter(Query.timestamp >= cutoff_date)\
                    .all()
                
                if not failed_results:
                    return {
                        'total_failures': 0,
                        'failure_rate': 0.0,
                        'common_errors': [],
                        'failure_patterns': []
                    }
                
                # Calculate failure rate
                total_commands = session.query(func.count(Result.id))\
                    .join(Query)\
                    .filter(Query.user_id == self.user_id)\
                    .filter(Query.timestamp >= cutoff_date)\
                    .scalar() or 0
                
                failure_rate = (len(failed_results) / total_commands * 100) if total_commands > 0 else 0
                
                # Analyze common errors
                error_patterns = defaultdict(int)
                command_patterns = defaultdict(int)
                
                for result in failed_results:
                    # Extract error type from stderr
                    error_text = result.stderr or ''
                    if error_text:
                        # Common error patterns
                        if 'permission denied' in error_text.lower():
                            error_patterns['permission_denied'] += 1
                        elif 'command not found' in error_text.lower():
                            error_patterns['command_not_found'] += 1
                        elif 'no such file' in error_text.lower():
                            error_patterns['file_not_found'] += 1
                        elif 'syntax error' in error_text.lower():
                            error_patterns['syntax_error'] += 1
                        else:
                            error_patterns['other'] += 1
                    
                    # Track command patterns
                    if result.command:
                        # Extract base command (first word)
                        base_cmd = result.command.split()[0] if result.command.split() else result.command
                        command_patterns[base_cmd] += 1
                
                # Get top error types
                common_errors = sorted(
                    error_patterns.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5]
                
                # Get top failing commands
                failing_commands = sorted(
                    command_patterns.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5]
                
                # Identify failure patterns
                patterns = []
                
                # Permission errors pattern
                if error_patterns.get('permission_denied', 0) > 0:
                    patterns.append({
                        'type': 'permission_issues',
                        'description': f"{error_patterns['permission_denied']} permission denied errors",
                        'suggestion': 'Check file permissions or use sudo for system commands',
                        'frequency': error_patterns['permission_denied']
                    })
                
                # Command not found pattern
                if error_patterns.get('command_not_found', 0) > 0:
                    patterns.append({
                        'type': 'missing_commands',
                        'description': f"{error_patterns['command_not_found']} command not found errors",
                        'suggestion': 'Install missing packages or check command spelling',
                        'frequency': error_patterns['command_not_found']
                    })
                
                # File not found pattern
                if error_patterns.get('file_not_found', 0) > 0:
                    patterns.append({
                        'type': 'file_path_issues',
                        'description': f"{error_patterns['file_not_found']} file not found errors",
                        'suggestion': 'Verify file paths before executing commands',
                        'frequency': error_patterns['file_not_found']
                    })
                
                return {
                    'total_failures': len(failed_results),
                    'failure_rate': failure_rate,
                    'common_errors': [{'error': k, 'count': v} for k, v in common_errors],
                    'failing_commands': [{'command': k, 'count': v} for k, v in failing_commands],
                    'failure_patterns': patterns
                }
        except Exception as e:
            logger.error(f"Error analyzing failure patterns: {e}")
            return {}
    
    def get_improved_suggestion(
        self,
        query_text: str,
        original_command: str,
        failure_reason: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get improved suggestion based on past failures."""
        try:
            # Analyze similar past failures
            with self.db.session() as session:
                # Find similar queries that failed
                similar_failures = session.query(Result)\
                    .join(Query)\
                    .filter(Query.user_id == self.user_id)\
                    .filter(Result.success == False)\
                    .filter(Query.query_text.like(f"%{query_text[:20]}%"))\
                    .order_by(Query.timestamp.desc())\
                    .limit(5)\
                    .all()
                
                if not similar_failures:
                    return None
                
                # Analyze common failure reasons
                failure_reasons = [r.stderr for r in similar_failures if r.stderr]
                
                # Generate improved suggestion
                improvements = []
                
                # Check for permission issues
                if any('permission' in r.lower() for r in failure_reasons):
                    improvements.append({
                        'type': 'permission_fix',
                        'suggestion': 'Try with sudo or check file permissions',
                        'confidence': 0.8
                    })
                
                # Check for command not found
                if any('not found' in r.lower() for r in failure_reasons):
                    improvements.append({
                        'type': 'command_fix',
                        'suggestion': 'Verify command exists or install required package',
                        'confidence': 0.9
                    })
                
                # Check for file path issues
                if any('no such file' in r.lower() or 'file not found' in r.lower() for r in failure_reasons):
                    improvements.append({
                        'type': 'path_fix',
                        'suggestion': 'Verify file path exists before executing',
                        'confidence': 0.85
                    })
                
                if improvements:
                    return {
                        'original_command': original_command,
                        'improvements': improvements,
                        'based_on_failures': len(similar_failures)
                    }
        except Exception as e:
            logger.error(f"Error getting improved suggestion: {e}")
        
        return None
    
    def learn_from_failure(
        self,
        query_text: str,
        command: str,
        failure_reason: str,
        successful_alternative: Optional[str] = None
    ):
        """Learn from a failure and successful alternative."""
        try:
            with self.db.session() as session:
                # Create or update pattern
                pattern = session.query(Pattern)\
                    .filter_by(user_id=self.user_id)\
                    .filter(Pattern.pattern_type == 'failure_learning')\
                    .filter(Pattern.pattern_data['query'].astext == query_text[:50])\
                    .first()
                
                if pattern:
                    # Update existing pattern
                    pattern_data = pattern.pattern_data or {}
                    pattern_data['failures'] = pattern_data.get('failures', 0) + 1
                    pattern_data['last_failure'] = datetime.now().isoformat()
                    pattern_data['failure_reason'] = failure_reason
                    
                    if successful_alternative:
                        pattern_data['successful_alternative'] = successful_alternative
                        pattern_data['successes'] = pattern_data.get('successes', 0) + 1
                    
                    pattern.pattern_data = pattern_data
                    pattern.frequency += 1
                    pattern.last_seen = datetime.now()
                else:
                    # Create new pattern
                    pattern_data = {
                        'query': query_text[:50],
                        'command': command,
                        'failures': 1,
                        'last_failure': datetime.now().isoformat(),
                        'failure_reason': failure_reason
                    }
                    
                    if successful_alternative:
                        pattern_data['successful_alternative'] = successful_alternative
                        pattern_data['successes'] = 1
                    
                    pattern = Pattern(
                        user_id=self.user_id,
                        pattern_type='failure_learning',
                        pattern_data=pattern_data,
                        frequency=1,
                        confidence=0.5
                    )
                    session.add(pattern)
                
                session.commit()
                logger.debug(f"Learned from failure: {command[:50]}")
        except Exception as e:
            logger.error(f"Error learning from failure: {e}")
    
    def get_failure_statistics(self) -> Dict[str, Any]:
        """Get overall failure statistics."""
        try:
            with self.db.session() as session:
                # Total failures
                total_failures = session.query(func.count(Result.id))\
                    .join(Query)\
                    .filter(Query.user_id == self.user_id)\
                    .filter(Result.success == False)\
                    .scalar() or 0
                
                # Total commands
                total_commands = session.query(func.count(Result.id))\
                    .join(Query)\
                    .filter(Query.user_id == self.user_id)\
                    .scalar() or 0
                
                # Recent failures (last 7 days)
                recent_cutoff = datetime.now() - timedelta(days=7)
                recent_failures = session.query(func.count(Result.id))\
                    .join(Query)\
                    .filter(Query.user_id == self.user_id)\
                    .filter(Result.success == False)\
                    .filter(Query.timestamp >= recent_cutoff)\
                    .scalar() or 0
                
                # Failure rate
                failure_rate = (total_failures / total_commands * 100) if total_commands > 0 else 0
                
                # Learned patterns
                learned_patterns = session.query(func.count(Pattern.id))\
                    .filter_by(user_id=self.user_id)\
                    .filter(Pattern.pattern_type == 'failure_learning')\
                    .scalar() or 0
                
                return {
                    'total_failures': total_failures,
                    'total_commands': total_commands,
                    'failure_rate': failure_rate,
                    'recent_failures': recent_failures,
                    'learned_patterns': learned_patterns
                }
        except Exception as e:
            logger.error(f"Error getting failure statistics: {e}")
            return {}

