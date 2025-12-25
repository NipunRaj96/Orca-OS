"""
Analytics engine for tracking user behavior and patterns.
Collects command usage, time patterns, and productivity metrics.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from sqlalchemy import func, and_, Integer

from ...database.session import DatabaseSession
from ...database.models import Query, Result, Pattern, Session as DBSession
from ...database.init_db import initialize_database

logger = logging.getLogger(__name__)


class AnalyticsEngine:
    """Analytics engine for user behavior tracking."""
    
    def __init__(self, user_id: str = "default"):
        """Initialize analytics engine."""
        initialize_database()
        self.db = DatabaseSession()
        self.user_id = user_id
    
    def track_command(
        self,
        query_text: str,
        command: Optional[str] = None,
        success: bool = True,
        execution_time: Optional[float] = None,
        context: Optional[Dict] = None
    ):
        """Track a command execution."""
        try:
            with self.db.session() as session:
                # Get or create current session
                current_session = session.query(DBSession)\
                    .filter_by(user_id=self.user_id)\
                    .filter(DBSession.ended_at.is_(None))\
                    .order_by(DBSession.started_at.desc())\
                    .first()
                
                if not current_session:
                    current_session = DBSession(
                        session_id=f"session_{datetime.now().timestamp()}",
                        user_id=self.user_id,
                        started_at=datetime.now()
                    )
                    session.add(current_session)
                    session.commit()
                
                # Serialize context data (handle datetime objects)
                import json
                from datetime import datetime
                def serialize_for_json(obj):
                    """Recursively serialize objects for JSON storage."""
                    if isinstance(obj, datetime):
                        return obj.isoformat()
                    elif isinstance(obj, dict):
                        return {k: serialize_for_json(v) for k, v in obj.items()}
                    elif isinstance(obj, (list, tuple)):
                        return [serialize_for_json(item) for item in obj]
                    elif hasattr(obj, '__dict__'):
                        return serialize_for_json(obj.__dict__)
                    return obj
                
                context_serialized = serialize_for_json(context) if context else {}
                
                # Create query record
                query = Query(
                    query_text=query_text,
                    user_id=self.user_id,
                    session_id=current_session.session_id,
                    context_data=context_serialized
                )
                session.add(query)
                session.flush()
                
                # Create result record if command exists
                if command:
                    result = Result(
                        query_id=query.id,
                        command=command,
                        success=success,
                        execution_time=execution_time
                    )
                    session.add(result)
                
                session.commit()
                logger.debug(f"Tracked command: {query_text[:50]}")
        except Exception as e:
            logger.error(f"Error tracking command: {e}")
    
    def get_usage_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get usage statistics for the last N days."""
        try:
            with self.db.session() as session:
                cutoff_date = datetime.now() - timedelta(days=days)
                
                # Total queries
                total_queries = session.query(func.count(Query.id))\
                    .filter_by(user_id=self.user_id)\
                    .filter(Query.timestamp >= cutoff_date)\
                    .scalar() or 0
                
                # Successful commands
                successful = session.query(func.count(Result.id))\
                    .join(Query)\
                    .filter(Query.user_id == self.user_id)\
                    .filter(Result.success == True)\
                    .filter(Query.timestamp >= cutoff_date)\
                    .scalar() or 0
                
                # Failed commands
                failed = session.query(func.count(Result.id))\
                    .join(Query)\
                    .filter(Query.user_id == self.user_id)\
                    .filter(Result.success == False)\
                    .filter(Query.timestamp >= cutoff_date)\
                    .scalar() or 0
                
                # Average execution time
                avg_time = session.query(func.avg(Result.execution_time))\
                    .join(Query)\
                    .filter(Query.user_id == self.user_id)\
                    .filter(Result.execution_time.isnot(None))\
                    .filter(Query.timestamp >= cutoff_date)\
                    .scalar() or 0.0
                
                # Commands by hour
                hour_distribution = defaultdict(int)
                queries_by_hour = session.query(
                    func.extract('hour', Query.timestamp).label('hour')
                ).filter_by(user_id=self.user_id)\
                 .filter(Query.timestamp >= cutoff_date).all()
                
                for row in queries_by_hour:
                    hour_distribution[int(row.hour)] += 1
                
                # Commands by day of week
                day_distribution = defaultdict(int)
                queries_by_day = session.query(
                    func.extract('dow', Query.timestamp).label('day')
                ).filter_by(user_id=self.user_id)\
                 .filter(Query.timestamp >= cutoff_date).all()
                
                for row in queries_by_day:
                    day_distribution[int(row.day)] += 1
                
                return {
                    'total_queries': total_queries,
                    'successful_commands': successful,
                    'failed_commands': failed,
                    'success_rate': (successful / (successful + failed) * 100) if (successful + failed) > 0 else 0,
                    'avg_execution_time': float(avg_time) if avg_time else 0.0,
                    'hour_distribution': dict(hour_distribution),
                    'day_distribution': dict(day_distribution),
                    'period_days': days
                }
        except Exception as e:
            logger.error(f"Error getting usage stats: {e}")
            return {}
    
    def get_command_frequency(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get most frequently used commands."""
        try:
            with self.db.session() as session:
                # Get command frequency
                command_freq = session.query(
                    Result.command,
                    func.count(Result.id).label('count'),
                    func.avg(Result.execution_time).label('avg_time'),
                    func.sum(func.cast(Result.success, Integer)).label('success_count')
                ).join(Query)\
                 .filter(Query.user_id == self.user_id)\
                 .filter(Result.command.isnot(None))\
                 .group_by(Result.command)\
                 .order_by(func.count(Result.id).desc())\
                 .limit(limit).all()
                
                results = []
                for cmd, count, avg_time, success_count in command_freq:
                    results.append({
                        'command': cmd,
                        'count': count,
                        'avg_time': float(avg_time) if avg_time else 0.0,
                        'success_rate': (success_count / count * 100) if count > 0 else 0
                    })
                
                return results
        except Exception as e:
            logger.error(f"Error getting command frequency: {e}")
            return []
    
    def get_productivity_metrics(self) -> Dict[str, Any]:
        """Calculate productivity metrics."""
        try:
            with self.db.session() as session:
                # Today's activity
                today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                today_queries = session.query(func.count(Query.id))\
                    .filter_by(user_id=self.user_id)\
                    .filter(Query.timestamp >= today_start)\
                    .scalar() or 0
                
                # This week's activity
                week_start = today_start - timedelta(days=today_start.weekday())
                week_queries = session.query(func.count(Query.id))\
                    .filter_by(user_id=self.user_id)\
                    .filter(Query.timestamp >= week_start)\
                    .scalar() or 0
                
                # Peak hours (most active hours)
                hour_activity = session.query(
                    func.extract('hour', Query.timestamp).label('hour'),
                    func.count(Query.id).label('count')
                ).filter_by(user_id=self.user_id)\
                 .filter(Query.timestamp >= datetime.now() - timedelta(days=30))\
                 .group_by(func.extract('hour', Query.timestamp))\
                 .order_by(func.count(Query.id).desc())\
                 .limit(3).all()
                
                peak_hours = [int(row.hour) for row in hour_activity]
                
                # Most productive day
                day_activity = session.query(
                    func.extract('dow', Query.timestamp).label('day'),
                    func.count(Query.id).label('count')
                ).filter_by(user_id=self.user_id)\
                 .filter(Query.timestamp >= datetime.now() - timedelta(days=30))\
                 .group_by(func.extract('dow', Query.timestamp))\
                 .order_by(func.count(Query.id).desc())\
                 .first()
                
                most_productive_day = int(day_activity.day) if day_activity else None
                day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                
                return {
                    'today_queries': today_queries,
                    'week_queries': week_queries,
                    'peak_hours': peak_hours,
                    'most_productive_day': day_names[most_productive_day] if most_productive_day is not None else None,
                    'avg_daily_queries': week_queries / 7 if week_queries > 0 else 0
                }
        except Exception as e:
            logger.error(f"Error getting productivity metrics: {e}")
            return {}
    
    def get_trends(self, days: int = 7) -> Dict[str, List[Any]]:
        """Get usage trends over time."""
        try:
            with self.db.session() as session:
                cutoff_date = datetime.now() - timedelta(days=days)
                
                # Daily query counts
                daily_counts = session.query(
                    func.date(Query.timestamp).label('date'),
                    func.count(Query.id).label('count')
                ).filter_by(user_id=self.user_id)\
                 .filter(Query.timestamp >= cutoff_date)\
                 .group_by(func.date(Query.timestamp))\
                 .order_by(func.date(Query.timestamp)).all()
                
                dates = []
                counts = []
                for row in daily_counts:
                    if hasattr(row.date, 'isoformat'):
                        dates.append(row.date.isoformat())
                    else:
                        dates.append(str(row.date))
                    counts.append(row.count)
                
                # Daily success rates
                daily_success = session.query(
                    func.date(Query.timestamp).label('date'),
                    func.avg(func.cast(Result.success, Integer)).label('success_rate')
                ).join(Query)\
                 .filter(Query.user_id == self.user_id)\
                 .filter(Query.timestamp >= cutoff_date)\
                 .group_by(func.date(Query.timestamp))\
                 .order_by(func.date(Query.timestamp)).all()
                
                success_rates = []
                for row in daily_success:
                    success_rates.append(float(row.success_rate * 100) if row.success_rate else 0)
                
                return {
                    'dates': dates,
                    'query_counts': counts,
                    'success_rates': success_rates
                }
        except Exception as e:
            logger.error(f"Error getting trends: {e}")
            return {'dates': [], 'query_counts': [], 'success_rates': []}

