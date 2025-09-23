#!/usr/bin/env python3
"""
Orca AI Scheduler
AI-aware process scheduling with intelligent resource allocation
"""

import asyncio
import psutil
import subprocess
import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import sys
from pathlib import Path

# Add orca-core to path
sys.path.insert(0, '/opt/orca-os')

from orca.llm.manager import LLMManager
from orca.core.models import UserQuery, SystemContext
from orca.utils.config import load_config


@dataclass
class ProcessProfile:
    """Process profile for AI scheduling decisions."""
    pid: int
    name: str
    cpu_usage: float
    memory_usage: float
    io_usage: float
    priority: int
    ai_importance: str
    ai_scheduling_hint: str
    resource_requirements: Dict[str, float]


class AIScheduler:
    """AI-aware process scheduler for Orca OS."""
    
    def __init__(self):
        """Initialize the AI scheduler."""
        self.config = load_config('/opt/orca-os/config/orca.yaml')
        self.llm_manager = LLMManager(self.config.llm.dict())
        self.process_profiles = {}
        self.scheduling_history = []
        self.optimization_running = False
        
        # System resource thresholds
        self.cpu_threshold = 80.0
        self.memory_threshold = 85.0
        self.io_threshold = 70.0
        
    async def analyze_process_importance(self, pid: int) -> str:
        """Analyze process importance using AI."""
        try:
            proc = psutil.Process(pid)
            proc_info = proc.as_dict(['name', 'cpu_percent', 'memory_percent', 'io_counters', 'nice'])
            
            # Get process context
            context = f"""
            Process: {proc_info['name']} (PID: {pid})
            CPU Usage: {proc_info['cpu_percent']}%
            Memory Usage: {proc_info['memory_percent']}%
            Priority: {proc_info['nice']}
            IO Counters: {proc_info['io_counters']}
            """
            
            # Query AI for importance assessment
            query = UserQuery(query=f"Assess the importance of this process for system operation: {context}")
            system_context = SystemContext(
                processes=[proc_info],
                memory_usage=psutil.virtual_memory().percent,
                cpu_usage=psutil.cpu_percent(),
                disk_usage=psutil.disk_usage('/').percent
            )
            
            suggestion = await self.llm_manager.generate_suggestion(query, system_context)
            
            # Parse AI response for importance level
            response = suggestion.explanation or ""
            if any(word in response.lower() for word in ['critical', 'essential', 'vital', 'system']):
                return 'critical'
            elif any(word in response.lower() for word in ['important', 'necessary', 'useful']):
                return 'important'
            elif any(word in response.lower() for word in ['optional', 'background', 'non-essential']):
                return 'optional'
            else:
                return 'normal'
                
        except Exception as e:
            print(f"Error analyzing process importance: {e}")
            return 'unknown'
    
    async def get_scheduling_recommendation(self, pid: int) -> str:
        """Get AI recommendation for process scheduling."""
        try:
            proc = psutil.Process(pid)
            proc_info = proc.as_dict(['name', 'cpu_percent', 'memory_percent', 'io_counters', 'nice'])
            
            # Get system context
            system_context = SystemContext(
                processes=[proc_info],
                memory_usage=psutil.virtual_memory().percent,
                cpu_usage=psutil.cpu_percent(),
                disk_usage=psutil.disk_usage('/').percent
            )
            
            # Query AI for scheduling recommendation
            query = UserQuery(query=f"Recommend optimal scheduling for this process: {proc_info['name']} (PID: {pid})")
            suggestion = await self.llm_manager.generate_suggestion(query, system_context)
            
            return suggestion.explanation or "No specific recommendation"
            
        except Exception as e:
            return f"Error getting scheduling recommendation: {e}"
    
    async def optimize_process_scheduling(self) -> Dict[str, Any]:
        """Optimize process scheduling based on AI analysis."""
        if self.optimization_running:
            return {"status": "already_running", "message": "Optimization already in progress"}
        
        self.optimization_running = True
        
        try:
            # Get all processes
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'nice', 'io_counters']):
                try:
                    proc_info = proc.info
                    if proc_info['pid'] and proc_info['name']:
                        processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Analyze each process
            optimizations = []
            for proc_info in processes:
                pid = proc_info['pid']
                name = proc_info['name']
                
                # Skip system processes
                if name in ['systemd', 'kernel', 'init', 'kthreadd']:
                    continue
                
                # Analyze importance
                importance = await self.analyze_process_importance(pid)
                
                # Get current priority
                current_priority = proc_info['nice']
                
                # Determine optimal priority based on AI analysis
                if importance == 'critical':
                    optimal_priority = -10  # High priority
                elif importance == 'important':
                    optimal_priority = 0    # Normal priority
                elif importance == 'optional':
                    optimal_priority = 10   # Low priority
                else:
                    optimal_priority = 0    # Default
                
                # Apply optimization if needed
                if current_priority != optimal_priority:
                    try:
                        subprocess.run(['sudo', 'renice', str(optimal_priority), str(pid)], 
                                     check=False, capture_output=True)
                        optimizations.append({
                            "pid": pid,
                            "name": name,
                            "old_priority": current_priority,
                            "new_priority": optimal_priority,
                            "importance": importance,
                            "status": "optimized"
                        })
                    except Exception as e:
                        optimizations.append({
                            "pid": pid,
                            "name": name,
                            "old_priority": current_priority,
                            "new_priority": optimal_priority,
                            "importance": importance,
                            "status": f"failed: {e}"
                        })
            
            # CPU affinity optimization
            cpu_optimizations = await self._optimize_cpu_affinity(processes)
            optimizations.extend(cpu_optimizations)
            
            return {
                "status": "completed",
                "optimizations": optimizations,
                "total_processes": len(processes),
                "optimized_processes": len([opt for opt in optimizations if opt['status'] == 'optimized']),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            self.optimization_running = False
    
    async def _optimize_cpu_affinity(self, processes: List[Dict]) -> List[Dict]:
        """Optimize CPU affinity for processes."""
        optimizations = []
        
        try:
            # Get CPU count
            cpu_count = psutil.cpu_count()
            if cpu_count <= 1:
                return optimizations
            
            # Find CPU-intensive processes
            cpu_intensive = [p for p in processes if p['cpu_percent'] and p['cpu_percent'] > 50]
            
            for proc in cpu_intensive:
                pid = proc['pid']
                name = proc['name']
                
                # Skip if already has CPU affinity set
                try:
                    current_affinity = psutil.Process(pid).cpu_affinity()
                    if current_affinity:
                        continue
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                
                # Set CPU affinity to spread load
                try:
                    # Distribute across available CPUs
                    cpu_list = list(range(cpu_count))
                    subprocess.run(['sudo', 'taskset', '-cp', ','.join(map(str, cpu_list)), str(pid)], 
                                 check=False, capture_output=True)
                    
                    optimizations.append({
                        "pid": pid,
                        "name": name,
                        "type": "cpu_affinity",
                        "cpus": cpu_list,
                        "status": "optimized"
                    })
                except Exception as e:
                    optimizations.append({
                        "pid": pid,
                        "name": name,
                        "type": "cpu_affinity",
                        "status": f"failed: {e}"
                    })
            
        except Exception as e:
            optimizations.append({
                "type": "cpu_affinity",
                "status": f"error: {e}"
            })
        
        return optimizations
    
    async def monitor_system_load(self) -> Dict[str, Any]:
        """Monitor system load and provide AI insights."""
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Get process load distribution
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    proc_info = proc.info
                    if proc_info['cpu_percent'] and proc_info['cpu_percent'] > 1.0:  # Only processes using >1% CPU
                        processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
            
            # Analyze load patterns
            load_analysis = await self._analyze_load_patterns(cpu_percent, memory.percent, disk.percent, processes)
            
            return {
                "cpu_usage": cpu_percent,
                "memory_usage": memory.percent,
                "disk_usage": disk.percent,
                "top_processes": processes[:10],  # Top 10 CPU users
                "load_analysis": load_analysis,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Failed to monitor system load: {str(e)}"}
    
    async def _analyze_load_patterns(self, cpu: float, memory: float, disk: float, processes: List[Dict]) -> Dict[str, Any]:
        """Analyze system load patterns with AI."""
        try:
            # Create context for AI analysis
            context = f"""
            System Load Analysis:
            CPU Usage: {cpu}%
            Memory Usage: {memory}%
            Disk Usage: {disk}%
            Top CPU Processes: {[p['name'] for p in processes[:5]]}
            """
            
            query = UserQuery(query=f"Analyze this system load and provide insights: {context}")
            system_context = SystemContext(
                processes=processes,
                memory_usage=memory,
                cpu_usage=cpu,
                disk_usage=disk
            )
            
            suggestion = await self.llm_manager.generate_suggestion(query, system_context)
            
            # Determine load status
            if cpu > 90 or memory > 95 or disk > 95:
                load_status = "critical"
            elif cpu > 70 or memory > 80 or disk > 85:
                load_status = "high"
            elif cpu > 50 or memory > 60 or disk > 70:
                load_status = "moderate"
            else:
                load_status = "normal"
            
            return {
                "load_status": load_status,
                "ai_insights": suggestion.explanation or "No specific insights available",
                "recommendations": await self._get_load_recommendations(cpu, memory, disk, processes)
            }
            
        except Exception as e:
            return {"error": f"Failed to analyze load patterns: {str(e)}"}
    
    async def _get_load_recommendations(self, cpu: float, memory: float, disk: float, processes: List[Dict]) -> List[str]:
        """Get AI recommendations for load optimization."""
        recommendations = []
        
        try:
            if cpu > 80:
                recommendations.append("High CPU usage detected. Consider closing unnecessary applications or optimizing running processes.")
            
            if memory > 85:
                recommendations.append("High memory usage. Check for memory leaks or consider adding more RAM.")
            
            if disk > 90:
                recommendations.append("Low disk space. Clean up unnecessary files or add more storage.")
            
            # Process-specific recommendations
            high_cpu_processes = [p for p in processes if p['cpu_percent'] and p['cpu_percent'] > 50]
            if high_cpu_processes:
                top_process = high_cpu_processes[0]
                recommendations.append(f"Process '{top_process['name']}' is using {top_process['cpu_percent']}% CPU. Consider investigating.")
            
            if not recommendations:
                recommendations.append("System load appears to be within normal parameters.")
                
        except Exception as e:
            recommendations.append(f"Error generating recommendations: {e}")
        
        return recommendations
    
    async def get_scheduling_report(self) -> Dict[str, Any]:
        """Get comprehensive scheduling report."""
        try:
            # Get current system state
            load_data = await self.monitor_system_load()
            
            # Get process distribution
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'nice']):
                try:
                    proc_info = proc.info
                    if proc_info['pid'] and proc_info['name']:
                        processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Analyze process priorities
            priority_distribution = {}
            for proc in processes:
                priority = proc['nice']
                if priority not in priority_distribution:
                    priority_distribution[priority] = 0
                priority_distribution[priority] += 1
            
            return {
                "system_load": load_data,
                "total_processes": len(processes),
                "priority_distribution": priority_distribution,
                "scheduling_efficiency": await self._calculate_scheduling_efficiency(processes),
                "recommendations": await self._get_system_scheduling_recommendations(load_data, processes),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Failed to generate scheduling report: {str(e)}"}
    
    async def _calculate_scheduling_efficiency(self, processes: List[Dict]) -> Dict[str, Any]:
        """Calculate scheduling efficiency metrics."""
        try:
            # Calculate CPU utilization efficiency
            total_cpu = sum(proc['cpu_percent'] or 0 for proc in processes)
            cpu_efficiency = min(100, total_cpu)  # Cap at 100%
            
            # Calculate priority distribution efficiency
            priorities = [proc['nice'] for proc in processes if proc['nice'] is not None]
            if priorities:
                priority_variance = sum((p - sum(priorities)/len(priorities))**2 for p in priorities) / len(priorities)
                priority_efficiency = max(0, 100 - priority_variance)  # Lower variance = higher efficiency
            else:
                priority_efficiency = 100
            
            return {
                "cpu_efficiency": cpu_efficiency,
                "priority_efficiency": priority_efficiency,
                "overall_efficiency": (cpu_efficiency + priority_efficiency) / 2
            }
            
        except Exception as e:
            return {"error": f"Failed to calculate scheduling efficiency: {str(e)}"}
    
    async def _get_system_scheduling_recommendations(self, load_data: Dict, processes: List[Dict]) -> List[str]:
        """Get system-wide scheduling recommendations."""
        recommendations = []
        
        try:
            if "load_analysis" in load_data and "load_status" in load_data["load_analysis"]:
                load_status = load_data["load_analysis"]["load_status"]
                
                if load_status == "critical":
                    recommendations.append("System load is critical. Consider immediate process optimization or system restart.")
                elif load_status == "high":
                    recommendations.append("High system load detected. Run process optimization to improve performance.")
                
            # Check for priority imbalances
            priorities = [proc['nice'] for proc in processes if proc['nice'] is not None]
            if priorities:
                high_priority_count = len([p for p in priorities if p < 0])
                if high_priority_count > len(priorities) * 0.3:  # More than 30% high priority
                    recommendations.append("Too many high-priority processes. Consider lowering priorities for non-critical processes.")
            
            if not recommendations:
                recommendations.append("Scheduling appears to be well-balanced. No immediate optimizations needed.")
                
        except Exception as e:
            recommendations.append(f"Error generating recommendations: {e}")
        
        return recommendations


async def main():
    """Main entry point for AI Scheduler."""
    scheduler = AIScheduler()
    
    print("🐋 Orca AI Scheduler")
    print("=" * 50)
    
    # Get scheduling report
    report = await scheduler.get_scheduling_report()
    
    if "error" in report:
        print(f"Error: {report['error']}")
        return
    
    print(f"Scheduling Report:")
    print(f"  Total Processes: {report['total_processes']}")
    print(f"  CPU Usage: {report['system_load']['cpu_usage']}%")
    print(f"  Memory Usage: {report['system_load']['memory_usage']}%")
    print(f"  Load Status: {report['system_load']['load_analysis']['load_status']}")
    
    if 'scheduling_efficiency' in report:
        efficiency = report['scheduling_efficiency']
        print(f"  Scheduling Efficiency: {efficiency['overall_efficiency']:.1f}%")
    
    print(f"\nRecommendations:")
    for rec in report['recommendations']:
        print(f"  • {rec}")


if __name__ == "__main__":
    asyncio.run(main())
