"""
Pattern recognition system for user behavior analytics.
Identifies usage patterns, productivity trends, and optimization opportunities.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from sqlalchemy import func, Integer

from ...database.session import DatabaseSession
from ...database.models import Query, Result, Pattern
from ...database.init_db import initialize_database

logger = logging.getLogger(__name__)


class PatternRecognizer:
    """Recognizes patterns in user behavior."""
    
    def __init__(self, user_id: str = "default"):
        """Initialize pattern recognizer."""
        initialize_database()
        self.db = DatabaseSession()
        self.user_id = user_id
    
    def identify_command_patterns(self, days: int = 30) -> List[Dict[str, Any]]:
        """Identify patterns in command usage."""
        try:
            with self.db.session() as session:
                cutoff_date = datetime.now() - timedelta(days=days)
                
                # Get command sequences (commands used together)
                queries = session.query(Query)\
                    .filter_by(user_id=self.user_id)\
                    .filter(Query.timestamp >= cutoff_date)\
                    .order_by(Query.timestamp)\
                    .all()
                
                # Find command pairs (commands used within 5 minutes)
                command_pairs = defaultdict(int)
                command_sequences = []
                
                for i, query in enumerate(queries):
                    results = session.query(Result)\
                        .filter_by(query_id=query.id)\
                        .all()
                    
                    for result in results:
                        if result.command:
                            command_sequences.append({
                                'command': result.command,
                                'timestamp': query.timestamp
                            })
                
                # Find frequent pairs
                for i in range(len(command_sequences) - 1):
                    cmd1 = command_sequences[i]['command']
                    cmd2 = command_sequences[i + 1]['command']
                    time_diff = (command_sequences[i + 1]['timestamp'] - 
                                command_sequences[i]['timestamp']).total_seconds()
                    
                    if time_diff < 300:  # Within 5 minutes
                        pair = f"{cmd1} → {cmd2}"
                        command_pairs[pair] += 1
                
                # Get top patterns
                patterns = []
                for pair, count in sorted(command_pairs.items(), key=lambda x: x[1], reverse=True)[:10]:
                    patterns.append({
                        'type': 'command_sequence',
                        'pattern': pair,
                        'frequency': count,
                        'confidence': min(count / len(command_sequences) * 100, 100) if command_sequences else 0
                    })
                
                return patterns
        except Exception as e:
            logger.error(f"Error identifying command patterns: {e}")
            return []
    
    def identify_time_patterns(self, days: int = 30) -> List[Dict[str, Any]]:
        """Identify time-based usage patterns."""
        try:
            with self.db.session() as session:
                cutoff_date = datetime.now() - timedelta(days=days)
                
                queries = session.query(Query)\
                    .filter_by(user_id=self.user_id)\
                    .filter(Query.timestamp >= cutoff_date)\
                    .all()
                
                # Hour patterns
                hour_counts = defaultdict(int)
                day_counts = defaultdict(int)
                
                for query in queries:
                    hour = query.timestamp.hour
                    day = query.timestamp.weekday()
                    hour_counts[hour] += 1
                    day_counts[day] += 1
                
                # Find peak hours (top 3)
                peak_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]
                
                # Find most active day
                most_active_day = max(day_counts.items(), key=lambda x: x[1]) if day_counts else None
                
                patterns = []
                
                # Peak hour pattern
                if peak_hours:
                    hours_str = ", ".join([f"{h}:00" for h, _ in peak_hours])
                    patterns.append({
                        'type': 'peak_hours',
                        'pattern': f"Most active during: {hours_str}",
                        'frequency': sum(count for _, count in peak_hours),
                        'confidence': 85.0
                    })
                
                # Active day pattern
                if most_active_day:
                    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    patterns.append({
                        'type': 'active_day',
                        'pattern': f"Most active on: {day_names[most_active_day[0]]}",
                        'frequency': most_active_day[1],
                        'confidence': 80.0
                    })
                
                return patterns
        except Exception as e:
            logger.error(f"Error identifying time patterns: {e}")
            return []
    
    def identify_productivity_trends(self, days: int = 30) -> Dict[str, Any]:
        """Identify productivity trends and opportunities."""
        try:
            with self.db.session() as session:
                cutoff_date = datetime.now() - timedelta(days=days)
                
                # Get daily productivity metrics
                daily_metrics = session.query(
                    func.date(Query.timestamp).label('date'),
                    func.count(Query.id).label('query_count'),
                    func.avg(func.cast(Result.success, Integer)).label('success_rate')
                ).join(Result, Query.id == Result.query_id)\
                 .filter(Query.user_id == self.user_id)\
                 .filter(Query.timestamp >= cutoff_date)\
                 .group_by(func.date(Query.timestamp))\
                 .all()
                
                if not daily_metrics:
                    return {}
                
                # Calculate trends
                query_counts = [m.query_count for m in daily_metrics]
                success_rates = [float(m.success_rate * 100) if m.success_rate else 0 for m in daily_metrics]
                
                # Trend direction
                if len(query_counts) >= 7:
                    recent_avg = sum(query_counts[-7:]) / 7
                    earlier_avg = sum(query_counts[:-7]) / (len(query_counts) - 7) if len(query_counts) > 7 else recent_avg
                    trend = "increasing" if recent_avg > earlier_avg else "decreasing" if recent_avg < earlier_avg else "stable"
                else:
                    trend = "insufficient_data"
                
                # Success rate trend
                if len(success_rates) >= 7:
                    recent_success = sum(success_rates[-7:]) / 7
                    earlier_success = sum(success_rates[:-7]) / (len(success_rates) - 7) if len(success_rates) > 7 else recent_success
                    success_trend = "improving" if recent_success > earlier_success else "declining" if recent_success < earlier_success else "stable"
                else:
                    success_trend = "insufficient_data"
                
                # Optimization opportunities
                opportunities = []
                
                # Low success rate opportunity
                avg_success = sum(success_rates) / len(success_rates) if success_rates else 0
                if avg_success < 80:
                    opportunities.append({
                        'type': 'success_rate',
                        'message': f"Success rate is {avg_success:.1f}%. Consider reviewing failed commands.",
                        'priority': 'high' if avg_success < 70 else 'medium'
                    })
                
                # Inconsistent usage opportunity
                if len(query_counts) >= 14:
                    variance = sum((x - sum(query_counts) / len(query_counts))**2 for x in query_counts) / len(query_counts)
                    if variance > 100:  # High variance
                        opportunities.append({
                            'type': 'consistency',
                            'message': "Usage is inconsistent. Regular usage improves Orca's learning.",
                            'priority': 'low'
                        })
                
                return {
                    'activity_trend': trend,
                    'success_trend': success_trend,
                    'avg_daily_queries': sum(query_counts) / len(query_counts) if query_counts else 0,
                    'avg_success_rate': avg_success,
                    'optimization_opportunities': opportunities
                }
        except Exception as e:
            logger.error(f"Error identifying productivity trends: {e}")
            return {}
    
    def generate_insights(self, days: int = 30) -> List[Dict[str, Any]]:
        """Generate actionable insights from patterns."""
        insights = []
        
        # Command patterns
        command_patterns = self.identify_command_patterns(days)
        if command_patterns:
            top_pattern = command_patterns[0]
            insights.append({
                'type': 'command_pattern',
                'title': 'Frequent Command Sequence',
                'message': f"You often use: {top_pattern['pattern']}",
                'suggestion': f"Consider creating a template or favorite for this sequence.",
                'priority': 'medium'
            })
        
        # Time patterns
        time_patterns = self.identify_time_patterns(days)
        for pattern in time_patterns:
            insights.append({
                'type': 'time_pattern',
                'title': 'Usage Pattern',
                'message': pattern['pattern'],
                'suggestion': 'Orca is learning your usage patterns to provide better suggestions.',
                'priority': 'low'
            })
        
        # Productivity trends
        trends = self.identify_productivity_trends(days)
        if trends:
            if trends.get('activity_trend') == 'increasing':
                insights.append({
                    'type': 'trend',
                    'title': 'Activity Trend',
                    'message': 'Your usage is increasing!',
                    'suggestion': 'Great! Orca is becoming more useful for your workflow.',
                    'priority': 'low'
                })
            
            opportunities = trends.get('optimization_opportunities', [])
            for opp in opportunities:
                insights.append({
                    'type': 'opportunity',
                    'title': 'Optimization Opportunity',
                    'message': opp['message'],
                    'suggestion': 'Review your command history to identify patterns.',
                    'priority': opp.get('priority', 'medium')
                })
        
        return insights

