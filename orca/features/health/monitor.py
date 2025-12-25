"""
Health Monitoring System for Orca OS.
Continuously monitors system health and tracks trends.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import deque

from .score_engine import HealthScoreEngine
from ...database.session import DatabaseSession
from ...database.init_db import initialize_database

logger = logging.getLogger(__name__)


class HealthMonitor:
    """Monitors system health continuously."""
    
    def __init__(self, db_session: Optional[DatabaseSession] = None):
        """Initialize health monitor."""
        initialize_database()
        self.db = db_session or DatabaseSession()
        self.score_engine = HealthScoreEngine()
        self.monitoring = False
        self.history = deque(maxlen=100)  # Keep last 100 scores
        self.alerts = []
    
    async def start_monitoring(self, interval: int = 300):
        """Start continuous health monitoring."""
        self.monitoring = True
        
        while self.monitoring:
            try:
                # Calculate current health score
                score_data = self.score_engine.calculate_overall_score()
                
                # Add to history
                self.history.append({
                    'timestamp': datetime.now(),
                    'score': score_data['overall_score'],
                    'status': score_data['status'],
                    'breakdown': score_data['breakdown']
                })
                
                # Check for alerts
                await self._check_alerts(score_data)
                
                # Save to database (optional)
                # await self._save_to_database(score_data)
                
                # Wait for next interval
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(interval)
    
    def stop_monitoring(self):
        """Stop health monitoring."""
        self.monitoring = False
    
    async def _check_alerts(self, score_data: Dict[str, Any]):
        """Check for health alerts."""
        score = score_data['overall_score']
        
        # Alert if score drops significantly
        if len(self.history) > 1:
            previous_score = self.history[-2]['score']
            if score < previous_score - 10:  # Drop of 10 points
                alert = {
                    'type': 'score_drop',
                    'message': f"Health score dropped from {previous_score:.1f} to {score:.1f}",
                    'severity': 'medium',
                    'timestamp': datetime.now()
                }
                self.alerts.append(alert)
                logger.warning(f"Health alert: {alert['message']}")
        
        # Alert if score is critically low
        if score < 50:
            alert = {
                'type': 'critical_score',
                'message': f"Health score is critically low: {score:.1f}",
                'severity': 'high',
                'timestamp': datetime.now()
            }
            self.alerts.append(alert)
            logger.error(f"Critical health alert: {alert['message']}")
    
    def get_current_health(self) -> Dict[str, Any]:
        """Get current health status."""
        return self.score_engine.calculate_overall_score()
    
    def get_health_trend(self, hours: int = 24) -> Dict[str, Any]:
        """Get health trend over time."""
        if not self.history:
            return {'error': 'No history available'}
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_scores = [
            entry for entry in self.history
            if entry['timestamp'] > cutoff_time
        ]
        
        if not recent_scores:
            return {'error': 'No recent history'}
        
        scores = [entry['score'] for entry in recent_scores]
        
        return {
            'period_hours': hours,
            'data_points': len(scores),
            'average_score': sum(scores) / len(scores),
            'min_score': min(scores),
            'max_score': max(scores),
            'trend': 'improving' if scores[-1] > scores[0] else 'declining' if scores[-1] < scores[0] else 'stable',
            'change': scores[-1] - scores[0]
        }
    
    def get_recent_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent health alerts."""
        return self.alerts[-limit:]
    
    def clear_alerts(self):
        """Clear all alerts."""
        self.alerts.clear()

