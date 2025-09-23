#!/usr/bin/env python3
"""
Orca AI Logging System
AI-assisted logging with intelligent summaries and analysis
"""

import asyncio
import subprocess
import json
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add orca-core to path
sys.path.insert(0, '/opt/orca-os')

from orca.llm.manager import LLMManager
from orca.core.models import UserQuery, SystemContext
from orca.utils.config import load_config


@dataclass
class LogEntry:
    """Structured log entry with AI analysis."""
    timestamp: str
    level: str
    service: str
    message: str
    ai_summary: str
    ai_priority: str
    ai_recommendation: str


class AILoggingSystem:
    """AI-assisted logging system for Orca OS."""
    
    def __init__(self):
        """Initialize the AI logging system."""
        self.config = load_config('/opt/orca-os/config/orca.yaml')
        self.llm_manager = LLMManager(self.config.llm.dict())
        self.log_patterns = {
            'error': r'(ERROR|CRITICAL|FATAL)',
            'warning': r'(WARN|WARNING)',
            'info': r'(INFO|NOTICE)',
            'debug': r'(DEBUG|TRACE)'
        }
        
    async def analyze_logs(self, service: str = None, hours: int = 24) -> List[LogEntry]:
        """Analyze system logs with AI insights."""
        try:
            # Get logs from journalctl
            cmd = ['journalctl', '--since', f'{hours}h ago', '--no-pager', '--output=json']
            if service:
                cmd.extend(['--unit', service])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                return []
            
            # Parse JSON logs
            logs = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        log_data = json.loads(line)
                        log_entry = await self._process_log_entry(log_data)
                        if log_entry:
                            logs.append(log_entry)
                    except json.JSONDecodeError:
                        continue
            
            return logs
            
        except Exception as e:
            print(f"Error analyzing logs: {e}")
            return []
    
    async def _process_log_entry(self, log_data: Dict) -> Optional[LogEntry]:
        """Process a single log entry with AI analysis."""
        try:
            # Extract basic information
            timestamp = log_data.get('__REALTIME_TIMESTAMP', '')
            if timestamp:
                timestamp = datetime.fromtimestamp(int(timestamp) / 1000000).isoformat()
            
            message = log_data.get('MESSAGE', '')
            service = log_data.get('_SYSTEMD_UNIT', log_data.get('SYSLOG_IDENTIFIER', 'unknown'))
            
            # Determine log level
            level = self._determine_log_level(message)
            
            # Get AI analysis
            ai_summary = await self._get_log_summary(message, service, level)
            ai_priority = await self._get_log_priority(message, service, level)
            ai_recommendation = await self._get_log_recommendation(message, service, level)
            
            return LogEntry(
                timestamp=timestamp,
                level=level,
                service=service,
                message=message,
                ai_summary=ai_summary,
                ai_priority=ai_priority,
                ai_recommendation=ai_recommendation
            )
            
        except Exception as e:
            print(f"Error processing log entry: {e}")
            return None
    
    def _determine_log_level(self, message: str) -> str:
        """Determine log level from message content."""
        message_upper = message.upper()
        
        if re.search(self.log_patterns['error'], message_upper):
            return 'error'
        elif re.search(self.log_patterns['warning'], message_upper):
            return 'warning'
        elif re.search(self.log_patterns['info'], message_upper):
            return 'info'
        elif re.search(self.log_patterns['debug'], message_upper):
            return 'debug'
        else:
            return 'info'
    
    async def _get_log_summary(self, message: str, service: str, level: str) -> str:
        """Get AI summary of log message."""
        try:
            context = f"""
            Service: {service}
            Level: {level}
            Message: {message}
            """
            
            query = UserQuery(query=f"Summarize this log entry: {context}")
            system_context = SystemContext(
                processes=[],
                memory_usage=0,
                cpu_usage=0,
                disk_usage=0
            )
            
            suggestion = await self.llm_manager.generate_suggestion(query, system_context)
            return suggestion.explanation or "No summary available"
            
        except Exception as e:
            return f"Summary error: {str(e)}"
    
    async def _get_log_priority(self, message: str, service: str, level: str) -> str:
        """Get AI-determined priority of log entry."""
        try:
            # High priority indicators
            high_priority_keywords = [
                'error', 'critical', 'fatal', 'panic', 'oom', 'out of memory',
                'failed', 'failure', 'exception', 'crash', 'segfault',
                'security', 'attack', 'intrusion', 'breach'
            ]
            
            # Medium priority indicators
            medium_priority_keywords = [
                'warning', 'warn', 'timeout', 'retry', 'retrying',
                'degraded', 'slow', 'performance', 'latency'
            ]
            
            message_lower = message.lower()
            
            if any(keyword in message_lower for keyword in high_priority_keywords):
                return 'high'
            elif any(keyword in message_lower for keyword in medium_priority_keywords):
                return 'medium'
            else:
                return 'low'
                
        except Exception:
            return 'unknown'
    
    async def _get_log_recommendation(self, message: str, service: str, level: str) -> str:
        """Get AI recommendation for log entry."""
        try:
            context = f"""
            Service: {service}
            Level: {level}
            Message: {message}
            """
            
            query = UserQuery(query=f"Provide a recommendation for this log entry: {context}")
            system_context = SystemContext(
                processes=[],
                memory_usage=0,
                cpu_usage=0,
                disk_usage=0
            )
            
            suggestion = await self.llm_manager.generate_suggestion(query, system_context)
            return suggestion.explanation or "No recommendation available"
            
        except Exception as e:
            return f"Recommendation error: {str(e)}"
    
    async def get_log_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get comprehensive log summary with AI insights."""
        try:
            logs = await self.analyze_logs(hours=hours)
            
            if not logs:
                return {"error": "No logs found"}
            
            # Categorize logs
            error_logs = [log for log in logs if log.level == 'error']
            warning_logs = [log for log in logs if log.level == 'warning']
            info_logs = [log for log in logs if log.level == 'info']
            
            # Get high priority logs
            high_priority_logs = [log for log in logs if log.ai_priority == 'high']
            
            # Get service breakdown
            services = {}
            for log in logs:
                service = log.service
                if service not in services:
                    services[service] = {'total': 0, 'errors': 0, 'warnings': 0}
                services[service]['total'] += 1
                if log.level == 'error':
                    services[service]['errors'] += 1
                elif log.level == 'warning':
                    services[service]['warnings'] += 1
            
            # Generate AI insights
            ai_insights = await self._generate_log_insights(logs)
            
            return {
                "summary": {
                    "total_logs": len(logs),
                    "error_logs": len(error_logs),
                    "warning_logs": len(warning_logs),
                    "info_logs": len(info_logs),
                    "high_priority_logs": len(high_priority_logs)
                },
                "services": services,
                "high_priority_logs": [
                    {
                        "timestamp": log.timestamp,
                        "service": log.service,
                        "level": log.level,
                        "message": log.message[:100] + "..." if len(log.message) > 100 else log.message,
                        "ai_summary": log.ai_summary,
                        "ai_recommendation": log.ai_recommendation
                    }
                    for log in high_priority_logs[:10]  # Top 10 high priority logs
                ],
                "ai_insights": ai_insights,
                "time_range": f"Last {hours} hours",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Failed to generate log summary: {str(e)}"}
    
    async def _generate_log_insights(self, logs: List[LogEntry]) -> List[str]:
        """Generate AI insights from log analysis."""
        insights = []
        
        try:
            # Analyze error patterns
            error_services = {}
            for log in logs:
                if log.level == 'error':
                    service = log.service
                    if service not in error_services:
                        error_services[service] = 0
                    error_services[service] += 1
            
            # Generate insights based on patterns
            if error_services:
                top_error_service = max(error_services, key=error_services.get)
                insights.append(f"Most error-prone service: {top_error_service} ({error_services[top_error_service]} errors)")
            
            # Check for recurring issues
            error_messages = [log.message for log in logs if log.level == 'error']
            if error_messages:
                # Simple pattern detection (in a real system, this would be more sophisticated)
                common_errors = {}
                for msg in error_messages:
                    # Extract key parts of error messages
                    key_parts = re.findall(r'\b\w+error\w+\b|\berror\b|\bfailed\b|\bfailure\b', msg.lower())
                    for part in key_parts:
                        if part not in common_errors:
                            common_errors[part] = 0
                        common_errors[part] += 1
                
                if common_errors:
                    most_common = max(common_errors, key=common_errors.get)
                    insights.append(f"Most common error type: {most_common} ({common_errors[most_common]} occurrences)")
            
            # System health insights
            total_logs = len(logs)
            error_rate = len([log for log in logs if log.level == 'error']) / total_logs if total_logs > 0 else 0
            
            if error_rate > 0.1:  # More than 10% errors
                insights.append(f"High error rate detected: {error_rate:.1%} of logs are errors")
            elif error_rate < 0.01:  # Less than 1% errors
                insights.append("System appears to be running smoothly with low error rate")
            
            # Time-based insights
            if logs:
                recent_logs = [log for log in logs if log.timestamp]
                if recent_logs:
                    # Check if errors are increasing
                    recent_errors = [log for log in recent_logs[-10:] if log.level == 'error']  # Last 10 logs
                    if len(recent_errors) > 5:
                        insights.append("Recent increase in errors detected - investigate immediately")
            
            if not insights:
                insights.append("No significant patterns detected in recent logs")
                
        except Exception as e:
            insights.append(f"Error generating insights: {str(e)}")
        
        return insights
    
    async def monitor_logs_realtime(self, callback=None):
        """Monitor logs in real-time with AI analysis."""
        try:
            # Use journalctl to follow logs
            process = subprocess.Popen(
                ['journalctl', '-f', '--output=json'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            print("🐋 Orca AI Log Monitor - Real-time Analysis")
            print("=" * 50)
            
            for line in process.stdout:
                if line.strip():
                    try:
                        log_data = json.loads(line)
                        log_entry = await self._process_log_entry(log_data)
                        
                        if log_entry and log_entry.ai_priority == 'high':
                            print(f"\n🚨 HIGH PRIORITY LOG:")
                            print(f"   Time: {log_entry.timestamp}")
                            print(f"   Service: {log_entry.service}")
                            print(f"   Level: {log_entry.level}")
                            print(f"   Message: {log_entry.message}")
                            print(f"   AI Summary: {log_entry.ai_summary}")
                            print(f"   AI Recommendation: {log_entry.ai_recommendation}")
                            print("-" * 50)
                            
                            if callback:
                                await callback(log_entry)
                                
                    except json.JSONDecodeError:
                        continue
                    except Exception as e:
                        print(f"Error processing log: {e}")
                        
        except KeyboardInterrupt:
            print("\nStopping log monitor...")
        except Exception as e:
            print(f"Error in log monitor: {e}")
        finally:
            if process:
                process.terminate()


async def main():
    """Main entry point for AI Logging System."""
    logging_system = AILoggingSystem()
    
    print("🐋 Orca AI Logging System")
    print("=" * 50)
    
    # Get log summary
    summary = await logging_system.get_log_summary(hours=24)
    
    if "error" in summary:
        print(f"Error: {summary['error']}")
        return
    
    print(f"Log Summary (Last 24 hours):")
    print(f"  Total Logs: {summary['summary']['total_logs']}")
    print(f"  Errors: {summary['summary']['error_logs']}")
    print(f"  Warnings: {summary['summary']['warning_logs']}")
    print(f"  High Priority: {summary['summary']['high_priority_logs']}")
    
    print(f"\nAI Insights:")
    for insight in summary['ai_insights']:
        print(f"  • {insight}")
    
    if summary['high_priority_logs']:
        print(f"\nHigh Priority Logs:")
        for log in summary['high_priority_logs'][:5]:  # Show top 5
            print(f"  • [{log['timestamp']}] {log['service']}: {log['message']}")


if __name__ == "__main__":
    asyncio.run(main())
