#!/usr/bin/env python3
"""
Orca OS System Dashboard
Comprehensive AI-powered system monitoring and control dashboard
"""

import asyncio
import psutil
import json
import time
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
class DashboardWidget:
    """Dashboard widget configuration."""
    name: str
    title: str
    type: str
    data: Dict[str, Any]
    refresh_interval: int
    ai_enhanced: bool


class OrcaDashboard:
    """AI-powered system dashboard for Orca OS."""
    
    def __init__(self):
        """Initialize the Orca dashboard."""
        self.config = load_config('/opt/orca-os/config/orca.yaml')
        self.llm_manager = LLMManager(self.config.llm.dict())
        self.widgets = {}
        self.refresh_interval = 5  # seconds
        self.running = False
        
    async def initialize_widgets(self):
        """Initialize all dashboard widgets."""
        # System Overview Widget
        self.widgets['system_overview'] = DashboardWidget(
            name='system_overview',
            title='System Overview',
            type='overview',
            data={},
            refresh_interval=5,
            ai_enhanced=True
        )
        
        # Process Monitor Widget
        self.widgets['process_monitor'] = DashboardWidget(
            name='process_monitor',
            title='Process Monitor',
            type='processes',
            data={},
            refresh_interval=3,
            ai_enhanced=True
        )
        
        # Resource Usage Widget
        self.widgets['resource_usage'] = DashboardWidget(
            name='resource_usage',
            title='Resource Usage',
            type='resources',
            data={},
            refresh_interval=2,
            ai_enhanced=False
        )
        
        # AI Insights Widget
        self.widgets['ai_insights'] = DashboardWidget(
            name='ai_insights',
            title='AI Insights',
            type='insights',
            data={},
            refresh_interval=10,
            ai_enhanced=True
        )
        
        # Log Monitor Widget
        self.widgets['log_monitor'] = DashboardWidget(
            name='log_monitor',
            title='Log Monitor',
            type='logs',
            data={},
            refresh_interval=5,
            ai_enhanced=True
        )
        
        # Predictive Alerts Widget
        self.widgets['predictive_alerts'] = DashboardWidget(
            name='predictive_alerts',
            title='Predictive Alerts',
            type='alerts',
            data={},
            refresh_interval=15,
            ai_enhanced=True
        )
    
    async def update_widget(self, widget_name: str) -> Dict[str, Any]:
        """Update a specific widget with fresh data."""
        if widget_name not in self.widgets:
            return {"error": f"Widget '{widget_name}' not found"}
        
        widget = self.widgets[widget_name]
        
        try:
            if widget.type == 'overview':
                data = await self._get_system_overview()
            elif widget.type == 'processes':
                data = await self._get_process_data()
            elif widget.type == 'resources':
                data = await self._get_resource_data()
            elif widget.type == 'insights':
                data = await self._get_ai_insights()
            elif widget.type == 'logs':
                data = await self._get_log_data()
            elif widget.type == 'alerts':
                data = await self._get_predictive_alerts()
            else:
                data = {"error": f"Unknown widget type: {widget.type}"}
            
            widget.data = data
            widget.data['last_updated'] = datetime.now().isoformat()
            
            return data
            
        except Exception as e:
            return {"error": f"Failed to update widget: {str(e)}"}
    
    async def _get_system_overview(self) -> Dict[str, Any]:
        """Get system overview data."""
        try:
            # Basic system info
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            
            # CPU info
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Memory info
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk info
            disk = psutil.disk_usage('/')
            
            # Network info
            network = psutil.net_io_counters()
            
            # Process count
            process_count = len(psutil.pids())
            
            # Get AI analysis
            ai_analysis = await self._analyze_system_health()
            
            return {
                "uptime": str(uptime).split('.')[0],  # Remove microseconds
                "boot_time": boot_time.isoformat(),
                "cpu": {
                    "percent": cpu_percent,
                    "count": cpu_count,
                    "frequency": cpu_freq.current if cpu_freq else None
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used
                },
                "swap": {
                    "total": swap.total,
                    "used": swap.used,
                    "percent": swap.percent
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": disk.percent
                },
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv
                },
                "processes": {
                    "count": process_count
                },
                "ai_analysis": ai_analysis
            }
            
        except Exception as e:
            return {"error": f"Failed to get system overview: {str(e)}"}
    
    async def _get_process_data(self) -> Dict[str, Any]:
        """Get process monitoring data."""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status', 'create_time']):
                try:
                    proc_info = proc.info
                    if proc_info['cpu_percent'] and proc_info['cpu_percent'] > 0.1:  # Only processes using >0.1% CPU
                        processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
            
            # Get AI insights for top processes
            ai_insights = []
            for proc in processes[:5]:  # Top 5 processes
                insight = await self._analyze_process(proc)
                ai_insights.append(insight)
            
            return {
                "processes": processes[:20],  # Top 20 processes
                "total_processes": len(processes),
                "ai_insights": ai_insights,
                "summary": {
                    "high_cpu": len([p for p in processes if p['cpu_percent'] and p['cpu_percent'] > 50]),
                    "high_memory": len([p for p in processes if p['memory_percent'] and p['memory_percent'] > 10]),
                    "zombie": len([p for p in processes if p['status'] == 'zombie'])
                }
            }
            
        except Exception as e:
            return {"error": f"Failed to get process data: {str(e)}"}
    
    async def _get_resource_data(self) -> Dict[str, Any]:
        """Get resource usage data."""
        try:
            # CPU usage over time
            cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
            cpu_avg = sum(cpu_percent) / len(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            # Network I/O
            network = psutil.net_io_counters()
            
            # Load average
            load_avg = psutil.getloadavg()
            
            return {
                "cpu": {
                    "percent": cpu_avg,
                    "per_core": cpu_percent,
                    "load_avg": load_avg
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used,
                    "cached": getattr(memory, 'cached', 0),
                    "buffers": getattr(memory, 'buffers', 0)
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": disk.percent
                },
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                }
            }
            
        except Exception as e:
            return {"error": f"Failed to get resource data: {str(e)}"}
    
    async def _get_ai_insights(self) -> Dict[str, Any]:
        """Get AI-powered system insights."""
        try:
            # Get current system state
            system_context = SystemContext(
                processes=[],
                memory_usage=psutil.virtual_memory().percent,
                cpu_usage=psutil.cpu_percent(),
                disk_usage=psutil.disk_usage('/').percent
            )
            
            # Generate AI insights
            query = UserQuery(query="Analyze the current system state and provide insights and recommendations")
            suggestion = await self.llm_manager.generate_suggestion(query, system_context)
            
            # Get specific recommendations
            recommendations = await self._get_system_recommendations()
            
            return {
                "ai_analysis": suggestion.explanation or "No AI analysis available",
                "recommendations": recommendations,
                "confidence": 0.85,  # Placeholder confidence score
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Failed to get AI insights: {str(e)}"}
    
    async def _get_log_data(self) -> Dict[str, Any]:
        """Get log monitoring data."""
        try:
            # This would integrate with the AI logging system
            # For now, return a simplified version
            
            return {
                "recent_errors": 0,  # Would be populated by AI logging system
                "recent_warnings": 0,
                "critical_issues": 0,
                "ai_insights": "Log analysis not available",
                "last_checked": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Failed to get log data: {str(e)}"}
    
    async def _get_predictive_alerts(self) -> Dict[str, Any]:
        """Get predictive alerts data."""
        try:
            # This would integrate with the predictive AI system
            # For now, return a simplified version
            
            return {
                "active_alerts": 0,  # Would be populated by predictive AI
                "predictions": [],
                "risk_level": "low",
                "recommendations": [],
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Failed to get predictive alerts: {str(e)}"}
    
    async def _analyze_system_health(self) -> Dict[str, Any]:
        """Analyze overall system health."""
        try:
            # Calculate health score
            health_score = 100
            
            # CPU health
            cpu_percent = psutil.cpu_percent()
            if cpu_percent > 90:
                health_score -= 30
            elif cpu_percent > 70:
                health_score -= 15
            
            # Memory health
            memory_percent = psutil.virtual_memory().percent
            if memory_percent > 95:
                health_score -= 30
            elif memory_percent > 80:
                health_score -= 15
            
            # Disk health
            disk_percent = psutil.disk_usage('/').percent
            if disk_percent > 95:
                health_score -= 20
            elif disk_percent > 85:
                health_score -= 10
            
            health_score = max(0, health_score)
            
            # Determine health status
            if health_score >= 90:
                status = "excellent"
            elif health_score >= 70:
                status = "good"
            elif health_score >= 50:
                status = "fair"
            else:
                status = "poor"
            
            return {
                "score": health_score,
                "status": status,
                "issues": self._identify_issues(cpu_percent, memory_percent, disk_percent)
            }
            
        except Exception as e:
            return {"error": f"Failed to analyze system health: {str(e)}"}
    
    def _identify_issues(self, cpu: float, memory: float, disk: float) -> List[str]:
        """Identify system issues."""
        issues = []
        
        if cpu > 90:
            issues.append("High CPU usage")
        if memory > 95:
            issues.append("High memory usage")
        if disk > 95:
            issues.append("Low disk space")
        
        if not issues:
            issues.append("No critical issues detected")
        
        return issues
    
    async def _analyze_process(self, proc_info: Dict) -> Dict[str, Any]:
        """Analyze a specific process."""
        try:
            # Simple analysis - in a real implementation, this would use AI
            analysis = {
                "pid": proc_info['pid'],
                "name": proc_info['name'],
                "cpu_usage": proc_info['cpu_percent'],
                "memory_usage": proc_info['memory_percent'],
                "status": proc_info['status'],
                "ai_insight": "Process appears normal",
                "recommendation": "No action needed"
            }
            
            # Add basic recommendations
            if proc_info['cpu_percent'] and proc_info['cpu_percent'] > 50:
                analysis["ai_insight"] = "High CPU usage detected"
                analysis["recommendation"] = "Consider investigating this process"
            elif proc_info['memory_percent'] and proc_info['memory_percent'] > 10:
                analysis["ai_insight"] = "High memory usage detected"
                analysis["recommendation"] = "Monitor for memory leaks"
            
            return analysis
            
        except Exception as e:
            return {"error": f"Failed to analyze process: {str(e)}"}
    
    async def _get_system_recommendations(self) -> List[Dict[str, Any]]:
        """Get system recommendations."""
        try:
            recommendations = []
            
            # CPU recommendations
            cpu_percent = psutil.cpu_percent()
            if cpu_percent > 80:
                recommendations.append({
                    "type": "cpu",
                    "priority": "high",
                    "message": "High CPU usage detected",
                    "action": "Close unnecessary applications or optimize running processes"
                })
            
            # Memory recommendations
            memory_percent = psutil.virtual_memory().percent
            if memory_percent > 85:
                recommendations.append({
                    "type": "memory",
                    "priority": "high",
                    "message": "High memory usage detected",
                    "action": "Free up memory or add more RAM"
                })
            
            # Disk recommendations
            disk_percent = psutil.disk_usage('/').percent
            if disk_percent > 90:
                recommendations.append({
                    "type": "disk",
                    "priority": "critical",
                    "message": "Low disk space",
                    "action": "Free up disk space immediately"
                })
            
            if not recommendations:
                recommendations.append({
                    "type": "general",
                    "priority": "low",
                    "message": "System running optimally",
                    "action": "No immediate action needed"
                })
            
            return recommendations
            
        except Exception as e:
            return [{"error": f"Failed to get recommendations: {str(e)}"}]
    
    async def start_dashboard(self):
        """Start the dashboard monitoring loop."""
        self.running = True
        print("🐋 Orca OS Dashboard Started")
        print("=" * 50)
        
        while self.running:
            try:
                # Update all widgets
                for widget_name in self.widgets:
                    await self.update_widget(widget_name)
                
                # Display dashboard
                await self._display_dashboard()
                
                # Wait for next refresh
                await asyncio.sleep(self.refresh_interval)
                
            except KeyboardInterrupt:
                print("\nStopping dashboard...")
                break
            except Exception as e:
                print(f"Error in dashboard loop: {e}")
                await asyncio.sleep(self.refresh_interval)
    
    async def _display_dashboard(self):
        """Display the dashboard."""
        # Clear screen (simple approach)
        print("\033[2J\033[H", end="")
        
        print("🐋 Orca OS System Dashboard")
        print("=" * 50)
        print(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # System Overview
        if 'system_overview' in self.widgets:
            data = self.widgets['system_overview'].data
            if 'error' not in data:
                print("📊 System Overview:")
                print(f"  Uptime: {data.get('uptime', 'Unknown')}")
                print(f"  CPU: {data.get('cpu', {}).get('percent', 0):.1f}%")
                print(f"  Memory: {data.get('memory', {}).get('percent', 0):.1f}%")
                print(f"  Disk: {data.get('disk', {}).get('percent', 0):.1f}%")
                print(f"  Processes: {data.get('processes', {}).get('count', 0)}")
                
                if 'ai_analysis' in data and 'status' in data['ai_analysis']:
                    print(f"  Health: {data['ai_analysis']['status'].upper()} ({data['ai_analysis']['score']}/100)")
                print()
        
        # Process Monitor
        if 'process_monitor' in self.widgets:
            data = self.widgets['process_monitor'].data
            if 'error' not in data and 'processes' in data:
                print("🔄 Top Processes:")
                for proc in data['processes'][:5]:
                    name = proc.get('name', 'Unknown')[:20]
                    cpu = proc.get('cpu_percent', 0)
                    memory = proc.get('memory_percent', 0)
                    print(f"  {name:<20} CPU: {cpu:5.1f}%  Memory: {memory:5.1f}%")
                print()
        
        # AI Insights
        if 'ai_insights' in self.widgets:
            data = self.widgets['ai_insights'].data
            if 'error' not in data and 'recommendations' in data:
                print("🤖 AI Recommendations:")
                for rec in data['recommendations'][:3]:
                    priority = rec.get('priority', 'low')
                    message = rec.get('message', 'No message')
                    print(f"  [{priority.upper()}] {message}")
                print()
        
        print("Press Ctrl+C to stop dashboard")
    
    def stop_dashboard(self):
        """Stop the dashboard."""
        self.running = False


async def main():
    """Main entry point for Orca Dashboard."""
    dashboard = OrcaDashboard()
    await dashboard.initialize_widgets()
    await dashboard.start_dashboard()


if __name__ == "__main__":
    asyncio.run(main())
