#!/usr/bin/env python3
"""
Orca AI Process Manager
AI-augmented process management with intelligent monitoring and optimization
"""

import asyncio
import psutil
import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import subprocess
import sys
from pathlib import Path

# Add orca-core to path
sys.path.insert(0, '/opt/orca-os')

from orca.llm.manager import LLMManager
from orca.core.models import UserQuery, SystemContext
from orca.utils.config import load_config


@dataclass
class ProcessInfo:
    """Enhanced process information with AI insights."""
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float
    status: str
    priority: int
    ai_insight: str
    ai_recommendation: str
    risk_level: str


class AIProcessManager:
    """AI-augmented process manager for Orca OS."""
    
    def __init__(self):
        """Initialize the AI process manager."""
        self.config = load_config('/opt/orca-os/config/orca.yaml')
        self.llm_manager = LLMManager(self.config.llm.dict())
        self.process_history = {}
        self.anomaly_threshold = 0.8
        self.optimization_running = False
        
    async def analyze_processes(self) -> List[ProcessInfo]:
        """Analyze all processes with AI insights."""
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status', 'nice']):
            try:
                pinfo = proc.info
                
                # Get AI insights for this process
                ai_insight = await self._get_process_insight(pinfo)
                ai_recommendation = await self._get_process_recommendation(pinfo)
                risk_level = self._assess_process_risk(pinfo)
                
                process_info = ProcessInfo(
                    pid=pinfo['pid'],
                    name=pinfo['name'],
                    cpu_percent=pinfo['cpu_percent'] or 0.0,
                    memory_percent=pinfo['memory_percent'] or 0.0,
                    status=pinfo['status'],
                    priority=pinfo['nice'],
                    ai_insight=ai_insight,
                    ai_recommendation=ai_recommendation,
                    risk_level=risk_level
                )
                
                processes.append(process_info)
                
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        return processes
    
    async def _get_process_insight(self, pinfo: Dict) -> str:
        """Get AI insight for a specific process."""
        try:
            # Create context about the process
            context = f"""
            Process: {pinfo['name']} (PID: {pinfo['pid']})
            CPU Usage: {pinfo['cpu_percent']}%
            Memory Usage: {pinfo['memory_percent']}%
            Status: {pinfo['status']}
            Priority: {pinfo['nice']}
            """
            
            # Query AI for insights
            query = UserQuery(query=f"Analyze this process and provide insights: {context}")
            system_context = SystemContext(
                processes=[pinfo],
                memory_usage=psutil.virtual_memory().percent,
                cpu_usage=psutil.cpu_percent(),
                disk_usage=psutil.disk_usage('/').percent
            )
            
            suggestion = await self.llm_manager.generate_suggestion(query, system_context)
            
            return suggestion.explanation or "No specific insights available"
            
        except Exception as e:
            return f"Analysis error: {str(e)}"
    
    async def _get_process_recommendation(self, pinfo: Dict) -> str:
        """Get AI recommendation for process optimization."""
        try:
            # Check if process is using excessive resources
            if pinfo['cpu_percent'] and pinfo['cpu_percent'] > 50:
                return "High CPU usage detected. Consider investigating for potential issues or optimization."
            elif pinfo['memory_percent'] and pinfo['memory_percent'] > 10:
                return "High memory usage. Monitor for memory leaks or consider if this process is necessary."
            elif pinfo['status'] == 'zombie':
                return "Zombie process detected. Consider cleaning up or investigating parent process."
            else:
                return "Process appears to be running normally."
                
        except Exception as e:
            return f"Recommendation error: {str(e)}"
    
    def _assess_process_risk(self, pinfo: Dict) -> str:
        """Assess risk level of a process."""
        try:
            risk_score = 0
            
            # High CPU usage
            if pinfo['cpu_percent'] and pinfo['cpu_percent'] > 80:
                risk_score += 3
            elif pinfo['cpu_percent'] and pinfo['cpu_percent'] > 50:
                risk_score += 2
            
            # High memory usage
            if pinfo['memory_percent'] and pinfo['memory_percent'] > 20:
                risk_score += 3
            elif pinfo['memory_percent'] and pinfo['memory_percent'] > 10:
                risk_score += 2
            
            # Zombie process
            if pinfo['status'] == 'zombie':
                risk_score += 4
            
            # System processes
            if pinfo['name'] in ['systemd', 'kernel', 'init']:
                risk_score = 0  # System processes are safe
            
            if risk_score >= 5:
                return "high"
            elif risk_score >= 3:
                return "medium"
            else:
                return "low"
                
        except Exception:
            return "unknown"
    
    async def optimize_system(self) -> Dict[str, Any]:
        """AI-powered system optimization."""
        if self.optimization_running:
            return {"status": "already_running", "message": "Optimization already in progress"}
        
        self.optimization_running = True
        
        try:
            # Analyze current system state
            processes = await self.analyze_processes()
            
            # Find optimization opportunities
            high_cpu_processes = [p for p in processes if p.cpu_percent > 50]
            high_memory_processes = [p for p in processes if p.memory_percent > 10]
            zombie_processes = [p for p in processes if p.status == 'zombie']
            
            optimizations = []
            
            # Clean up zombie processes
            if zombie_processes:
                for proc in zombie_processes:
                    try:
                        # Kill zombie processes
                        subprocess.run(['sudo', 'kill', '-9', str(proc.pid)], check=False)
                        optimizations.append(f"Cleaned up zombie process: {proc.name} (PID: {proc.pid})")
                    except Exception as e:
                        optimizations.append(f"Failed to clean zombie process {proc.name}: {e}")
            
            # Optimize high CPU processes
            for proc in high_cpu_processes:
                if proc.risk_level == "high":
                    try:
                        # Lower priority for non-critical high CPU processes
                        subprocess.run(['sudo', 'renice', '10', str(proc.pid)], check=False)
                        optimizations.append(f"Lowered priority for high CPU process: {proc.name}")
                    except Exception as e:
                        optimizations.append(f"Failed to optimize {proc.name}: {e}")
            
            # Memory optimization
            if psutil.virtual_memory().percent > 80:
                try:
                    # Clear page cache
                    subprocess.run(['sudo', 'sync'], check=False)
                    subprocess.run(['sudo', 'echo', '3', '>', '/proc/sys/vm/drop_caches'], shell=True, check=False)
                    optimizations.append("Cleared page cache to free memory")
                except Exception as e:
                    optimizations.append(f"Failed to clear page cache: {e}")
            
            return {
                "status": "completed",
                "optimizations": optimizations,
                "high_cpu_processes": len(high_cpu_processes),
                "high_memory_processes": len(high_memory_processes),
                "zombie_processes": len(zombie_processes)
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            self.optimization_running = False
    
    async def monitor_anomalies(self) -> List[Dict[str, Any]]:
        """Monitor for system anomalies using AI."""
        anomalies = []
        
        try:
            # Get current system state
            processes = await self.analyze_processes()
            
            # Check for unusual patterns
            for proc in processes:
                # Unusual CPU spike
                if proc.cpu_percent > 90:
                    anomalies.append({
                        "type": "high_cpu",
                        "process": proc.name,
                        "pid": proc.pid,
                        "value": proc.cpu_percent,
                        "severity": "critical",
                        "recommendation": "Investigate process for potential issues or malware"
                    })
                
                # Unusual memory usage
                if proc.memory_percent > 30:
                    anomalies.append({
                        "type": "high_memory",
                        "process": proc.name,
                        "pid": proc.pid,
                        "value": proc.memory_percent,
                        "severity": "warning",
                        "recommendation": "Check for memory leaks or unnecessary processes"
                    })
                
                # Zombie processes
                if proc.status == 'zombie':
                    anomalies.append({
                        "type": "zombie_process",
                        "process": proc.name,
                        "pid": proc.pid,
                        "severity": "medium",
                        "recommendation": "Clean up zombie process"
                    })
            
            # System-level anomalies
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                anomalies.append({
                    "type": "system_memory",
                    "value": memory.percent,
                    "severity": "critical",
                    "recommendation": "Free up memory or add more RAM"
                })
            
            disk = psutil.disk_usage('/')
            if disk.percent > 90:
                anomalies.append({
                    "type": "disk_space",
                    "value": disk.percent,
                    "severity": "critical",
                    "recommendation": "Free up disk space immediately"
                })
            
        except Exception as e:
            anomalies.append({
                "type": "monitoring_error",
                "severity": "low",
                "message": f"Error monitoring system: {e}"
            })
        
        return anomalies
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health report."""
        try:
            processes = await self.analyze_processes()
            anomalies = await self.monitor_anomalies()
            
            # Calculate health score
            health_score = 100
            
            # Deduct points for issues
            for anomaly in anomalies:
                if anomaly['severity'] == 'critical':
                    health_score -= 20
                elif anomaly['severity'] == 'warning':
                    health_score -= 10
                elif anomaly['severity'] == 'medium':
                    health_score -= 5
            
            health_score = max(0, health_score)
            
            # Determine health status
            if health_score >= 90:
                health_status = "excellent"
            elif health_score >= 70:
                health_status = "good"
            elif health_score >= 50:
                health_status = "fair"
            else:
                health_status = "poor"
            
            return {
                "health_score": health_score,
                "health_status": health_status,
                "total_processes": len(processes),
                "anomalies": anomalies,
                "timestamp": datetime.now().isoformat(),
                "recommendations": await self._get_system_recommendations(processes, anomalies)
            }
            
        except Exception as e:
            return {
                "health_score": 0,
                "health_status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _get_system_recommendations(self, processes: List[ProcessInfo], anomalies: List[Dict]) -> List[str]:
        """Get AI-powered system recommendations."""
        recommendations = []
        
        try:
            # Analyze system state
            high_cpu_count = len([p for p in processes if p.cpu_percent > 50])
            high_memory_count = len([p for p in processes if p.memory_percent > 10])
            zombie_count = len([p for p in processes if p.status == 'zombie'])
            
            if high_cpu_count > 5:
                recommendations.append("Multiple processes using high CPU. Consider system optimization.")
            
            if high_memory_count > 3:
                recommendations.append("Multiple processes using high memory. Check for memory leaks.")
            
            if zombie_count > 0:
                recommendations.append("Zombie processes detected. Run system cleanup.")
            
            # System-level recommendations
            memory = psutil.virtual_memory()
            if memory.percent > 80:
                recommendations.append("High memory usage. Consider closing unnecessary applications.")
            
            disk = psutil.disk_usage('/')
            if disk.percent > 85:
                recommendations.append("Low disk space. Clean up unnecessary files.")
            
            if not recommendations:
                recommendations.append("System is running optimally. No immediate actions needed.")
            
        except Exception as e:
            recommendations.append(f"Error generating recommendations: {e}")
        
        return recommendations


async def main():
    """Main entry point for AI Process Manager."""
    manager = AIProcessManager()
    
    print("🐋 Orca AI Process Manager")
    print("=" * 50)
    
    # Get system health
    health = await manager.get_system_health()
    print(f"System Health: {health['health_status'].upper()} ({health['health_score']}/100)")
    print(f"Total Processes: {health['total_processes']}")
    print(f"Anomalies: {len(health['anomalies'])}")
    
    # Show recommendations
    if 'recommendations' in health:
        print("\nRecommendations:")
        for rec in health['recommendations']:
            print(f"  • {rec}")
    
    # Show anomalies
    if health['anomalies']:
        print("\nAnomalies:")
        for anomaly in health['anomalies']:
            print(f"  • {anomaly['type']}: {anomaly.get('message', anomaly.get('recommendation', 'No details'))}")


if __name__ == "__main__":
    asyncio.run(main())
