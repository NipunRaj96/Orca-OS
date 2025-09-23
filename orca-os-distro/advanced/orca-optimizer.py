#!/usr/bin/env python3
"""
Orca OS System Optimizer
AI-powered system optimization and performance tuning
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
class OptimizationTask:
    """System optimization task."""
    name: str
    description: str
    category: str
    priority: str
    impact: str
    risk: str
    command: str
    ai_recommendation: str


class OrcaOptimizer:
    """AI-powered system optimizer for Orca OS."""
    
    def __init__(self):
        """Initialize the Orca optimizer."""
        self.config = load_config('/opt/orca-os/config/orca.yaml')
        self.llm_manager = LLMManager(self.config.llm.dict())
        self.optimization_history = []
        self.optimization_tasks = []
        
    async def initialize_optimization_tasks(self):
        """Initialize available optimization tasks."""
        self.optimization_tasks = [
            OptimizationTask(
                name="memory_cleanup",
                description="Clean up memory caches and buffers",
                category="memory",
                priority="medium",
                impact="medium",
                risk="low",
                command="sync && echo 3 > /proc/sys/vm/drop_caches",
                ai_recommendation="Safe memory cleanup that can free up cached memory"
            ),
            OptimizationTask(
                name="swap_optimization",
                description="Optimize swap usage",
                category="memory",
                priority="low",
                impact="low",
                risk="low",
                command="swapoff -a && swapon -a",
                ai_recommendation="Refreshes swap space to improve memory management"
            ),
            OptimizationTask(
                name="process_priority_optimization",
                description="Optimize process priorities",
                category="processes",
                priority="high",
                impact="high",
                risk="medium",
                command="orca-scheduler --optimize",
                ai_recommendation="Uses AI to optimize process scheduling and priorities"
            ),
            OptimizationTask(
                name="log_cleanup",
                description="Clean up old log files",
                category="storage",
                priority="medium",
                impact="medium",
                risk="low",
                command="journalctl --vacuum-time=7d",
                ai_recommendation="Removes log files older than 7 days to free disk space"
            ),
            OptimizationTask(
                name="package_cleanup",
                description="Clean up unused packages",
                category="storage",
                priority="medium",
                impact="medium",
                risk="low",
                command="apt autoremove -y && apt autoclean",
                ai_recommendation="Removes unused packages and cleans package cache"
            ),
            OptimizationTask(
                name="temp_cleanup",
                description="Clean up temporary files",
                category="storage",
                priority="high",
                impact="medium",
                risk="low",
                command="find /tmp -type f -atime +7 -delete",
                ai_recommendation="Removes temporary files older than 7 days"
            ),
            OptimizationTask(
                name="network_optimization",
                description="Optimize network settings",
                category="network",
                priority="low",
                impact="low",
                risk="low",
                command="sysctl -w net.core.rmem_max=16777216",
                ai_recommendation="Increases network receive buffer size for better performance"
            ),
            OptimizationTask(
                name="cpu_governor_optimization",
                description="Set CPU governor to performance mode",
                category="cpu",
                priority="medium",
                impact="high",
                risk="medium",
                command="echo performance | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor",
                ai_recommendation="Sets CPU to performance mode for better responsiveness"
            )
        ]
    
    async def analyze_system(self) -> Dict[str, Any]:
        """Analyze system for optimization opportunities."""
        try:
            # Get current system state
            system_context = await self._get_system_context()
            
            # Analyze different aspects
            memory_analysis = await self._analyze_memory()
            storage_analysis = await self._analyze_storage()
            process_analysis = await self._analyze_processes()
            network_analysis = await self._analyze_network()
            cpu_analysis = await self._analyze_cpu()
            
            # Get AI recommendations
            ai_recommendations = await self._get_ai_recommendations(
                memory_analysis, storage_analysis, process_analysis, 
                network_analysis, cpu_analysis
            )
            
            return {
                "memory": memory_analysis,
                "storage": storage_analysis,
                "processes": process_analysis,
                "network": network_analysis,
                "cpu": cpu_analysis,
                "ai_recommendations": ai_recommendations,
                "overall_score": self._calculate_optimization_score(
                    memory_analysis, storage_analysis, process_analysis,
                    network_analysis, cpu_analysis
                ),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Failed to analyze system: {str(e)}"}
    
    async def _get_system_context(self) -> SystemContext:
        """Get current system context."""
        try:
            # Get system metrics
            memory = psutil.virtual_memory()
            cpu = psutil.cpu_percent()
            disk = psutil.disk_usage('/')
            
            # Get running processes
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    proc_info = proc.info
                    if proc_info['cpu_percent'] and proc_info['cpu_percent'] > 1.0:
                        processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return SystemContext(
                processes=processes,
                memory_usage=memory.percent,
                cpu_usage=cpu,
                disk_usage=disk.percent
            )
            
        except Exception as e:
            return SystemContext(
                processes=[],
                memory_usage=0,
                cpu_usage=0,
                disk_usage=0
            )
    
    async def _analyze_memory(self) -> Dict[str, Any]:
        """Analyze memory usage and optimization opportunities."""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Calculate memory pressure
            memory_pressure = memory.percent
            swap_usage = swap.percent
            
            # Determine optimization needs
            needs_optimization = []
            if memory_pressure > 80:
                needs_optimization.append("High memory usage - consider cleanup")
            if swap_usage > 50:
                needs_optimization.append("High swap usage - consider memory upgrade")
            
            # Check for memory leaks
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
                try:
                    proc_info = proc.info
                    if proc_info['memory_percent'] and proc_info['memory_percent'] > 10:
                        processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return {
                "memory_percent": memory_pressure,
                "swap_percent": swap_usage,
                "available_memory": memory.available,
                "total_memory": memory.total,
                "needs_optimization": needs_optimization,
                "high_memory_processes": processes,
                "optimization_score": max(0, 100 - memory_pressure)
            }
            
        except Exception as e:
            return {"error": f"Failed to analyze memory: {str(e)}"}
    
    async def _analyze_storage(self) -> Dict[str, Any]:
        """Analyze storage usage and optimization opportunities."""
        try:
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Check for large files (simplified)
            needs_optimization = []
            if disk_percent > 90:
                needs_optimization.append("Critical disk space - immediate cleanup needed")
            elif disk_percent > 80:
                needs_optimization.append("Low disk space - consider cleanup")
            
            # Check for log files
            try:
                log_size = subprocess.run(
                    ['du', '-sh', '/var/log'],
                    capture_output=True, text=True, timeout=10
                )
                log_size_str = log_size.stdout.split()[0] if log_size.returncode == 0 else "Unknown"
            except:
                log_size_str = "Unknown"
            
            return {
                "disk_percent": disk_percent,
                "free_space": disk.free,
                "total_space": disk.total,
                "log_size": log_size_str,
                "needs_optimization": needs_optimization,
                "optimization_score": max(0, 100 - disk_percent)
            }
            
        except Exception as e:
            return {"error": f"Failed to analyze storage: {str(e)}"}
    
    async def _analyze_processes(self) -> Dict[str, Any]:
        """Analyze process usage and optimization opportunities."""
        try:
            processes = []
            total_cpu = 0
            total_memory = 0
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'nice']):
                try:
                    proc_info = proc.info
                    if proc_info['cpu_percent'] and proc_info['cpu_percent'] > 0.1:
                        processes.append(proc_info)
                        total_cpu += proc_info['cpu_percent'] or 0
                        total_memory += proc_info['memory_percent'] or 0
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
            
            # Analyze process efficiency
            needs_optimization = []
            if total_cpu > 200:  # More than 200% CPU across all processes
                needs_optimization.append("High CPU usage across processes")
            if total_memory > 150:  # More than 150% memory usage
                needs_optimization.append("High memory usage across processes")
            
            # Check for zombie processes
            zombie_count = len([p for p in processes if p.get('status') == 'zombie'])
            if zombie_count > 0:
                needs_optimization.append(f"{zombie_count} zombie processes detected")
            
            return {
                "total_processes": len(processes),
                "total_cpu_usage": total_cpu,
                "total_memory_usage": total_memory,
                "zombie_processes": zombie_count,
                "top_processes": processes[:10],
                "needs_optimization": needs_optimization,
                "optimization_score": max(0, 100 - min(total_cpu, 100))
            }
            
        except Exception as e:
            return {"error": f"Failed to analyze processes: {str(e)}"}
    
    async def _analyze_network(self) -> Dict[str, Any]:
        """Analyze network usage and optimization opportunities."""
        try:
            network = psutil.net_io_counters()
            
            # Basic network analysis
            needs_optimization = []
            
            # Check for high network usage (simplified)
            if network.bytes_sent > 1000000000:  # More than 1GB sent
                needs_optimization.append("High network usage detected")
            
            return {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv,
                "needs_optimization": needs_optimization,
                "optimization_score": 85  # Default good score
            }
            
        except Exception as e:
            return {"error": f"Failed to analyze network: {str(e)}"}
    
    async def _analyze_cpu(self) -> Dict[str, Any]:
        """Analyze CPU usage and optimization opportunities."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Check CPU load
            load_avg = psutil.getloadavg()
            load_per_core = [load / cpu_count for load in load_avg]
            
            needs_optimization = []
            if cpu_percent > 80:
                needs_optimization.append("High CPU usage - consider optimization")
            if load_per_core[0] > 1.0:  # Load average > 1 per core
                needs_optimization.append("High system load - consider process optimization")
            
            return {
                "cpu_percent": cpu_percent,
                "cpu_count": cpu_count,
                "cpu_frequency": cpu_freq.current if cpu_freq else None,
                "load_average": load_avg,
                "load_per_core": load_per_core,
                "needs_optimization": needs_optimization,
                "optimization_score": max(0, 100 - cpu_percent)
            }
            
        except Exception as e:
            return {"error": f"Failed to analyze CPU: {str(e)}"}
    
    async def _get_ai_recommendations(self, memory_analysis, storage_analysis, 
                                    process_analysis, network_analysis, cpu_analysis) -> List[Dict[str, Any]]:
        """Get AI-powered optimization recommendations."""
        try:
            # Create context for AI analysis
            context = f"""
            Memory Usage: {memory_analysis.get('memory_percent', 0)}%
            Disk Usage: {storage_analysis.get('disk_percent', 0)}%
            CPU Usage: {cpu_analysis.get('cpu_percent', 0)}%
            Process Count: {process_analysis.get('total_processes', 0)}
            Memory Issues: {memory_analysis.get('needs_optimization', [])}
            Storage Issues: {storage_analysis.get('needs_optimization', [])}
            Process Issues: {process_analysis.get('needs_optimization', [])}
            """
            
            query = UserQuery(query=f"Provide system optimization recommendations: {context}")
            system_context = SystemContext(
                processes=[],
                memory_usage=memory_analysis.get('memory_percent', 0),
                cpu_usage=cpu_analysis.get('cpu_percent', 0),
                disk_usage=storage_analysis.get('disk_percent', 0)
            )
            
            suggestion = await self.llm_manager.generate_suggestion(query, system_context)
            
            # Parse AI response and create recommendations
            recommendations = []
            
            # Memory recommendations
            if memory_analysis.get('memory_percent', 0) > 80:
                recommendations.append({
                    "category": "memory",
                    "priority": "high",
                    "action": "memory_cleanup",
                    "description": "Clean up memory caches and buffers",
                    "ai_insight": suggestion.explanation or "High memory usage detected"
                })
            
            # Storage recommendations
            if storage_analysis.get('disk_percent', 0) > 80:
                recommendations.append({
                    "category": "storage",
                    "priority": "high",
                    "action": "log_cleanup",
                    "description": "Clean up old log files",
                    "ai_insight": "Low disk space - clean up logs and temporary files"
                })
            
            # Process recommendations
            if process_analysis.get('total_cpu_usage', 0) > 200:
                recommendations.append({
                    "category": "processes",
                    "priority": "medium",
                    "action": "process_priority_optimization",
                    "description": "Optimize process priorities",
                    "ai_insight": "High CPU usage across processes - optimize scheduling"
                })
            
            return recommendations
            
        except Exception as e:
            return [{"error": f"Failed to get AI recommendations: {str(e)}"}]
    
    def _calculate_optimization_score(self, memory_analysis, storage_analysis, 
                                    process_analysis, network_analysis, cpu_analysis) -> int:
        """Calculate overall optimization score."""
        try:
            scores = []
            
            if 'optimization_score' in memory_analysis:
                scores.append(memory_analysis['optimization_score'])
            if 'optimization_score' in storage_analysis:
                scores.append(storage_analysis['optimization_score'])
            if 'optimization_score' in process_analysis:
                scores.append(process_analysis['optimization_score'])
            if 'optimization_score' in network_analysis:
                scores.append(network_analysis['optimization_score'])
            if 'optimization_score' in cpu_analysis:
                scores.append(cpu_analysis['optimization_score'])
            
            if scores:
                return sum(scores) // len(scores)
            else:
                return 50  # Default score
                
        except Exception:
            return 50
    
    async def get_optimization_plan(self) -> List[OptimizationTask]:
        """Get recommended optimization plan."""
        try:
            # Analyze system first
            analysis = await self.analyze_system()
            
            if "error" in analysis:
                return []
            
            # Select tasks based on analysis
            recommended_tasks = []
            
            # Memory tasks
            if analysis['memory'].get('memory_percent', 0) > 80:
                recommended_tasks.append(self.optimization_tasks[0])  # memory_cleanup
                recommended_tasks.append(self.optimization_tasks[1])  # swap_optimization
            
            # Storage tasks
            if analysis['storage'].get('disk_percent', 0) > 80:
                recommended_tasks.append(self.optimization_tasks[3])  # log_cleanup
                recommended_tasks.append(self.optimization_tasks[4])  # package_cleanup
                recommended_tasks.append(self.optimization_tasks[5])  # temp_cleanup
            
            # Process tasks
            if analysis['processes'].get('total_cpu_usage', 0) > 200:
                recommended_tasks.append(self.optimization_tasks[2])  # process_priority_optimization
            
            # CPU tasks
            if analysis['cpu'].get('cpu_percent', 0) > 70:
                recommended_tasks.append(self.optimization_tasks[7])  # cpu_governor_optimization
            
            # Network tasks (always include for completeness)
            recommended_tasks.append(self.optimization_tasks[6])  # network_optimization
            
            return recommended_tasks
            
        except Exception as e:
            print(f"Error getting optimization plan: {e}")
            return []
    
    async def execute_optimization(self, task: OptimizationTask, dry_run: bool = False) -> Dict[str, Any]:
        """Execute an optimization task."""
        try:
            if dry_run:
                return {
                    "status": "dry_run",
                    "task": task.name,
                    "command": task.command,
                    "description": task.description,
                    "ai_recommendation": task.ai_recommendation
                }
            
            # Execute the command
            result = subprocess.run(
                task.command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            # Record optimization
            optimization_record = {
                "task": task.name,
                "command": task.command,
                "timestamp": datetime.now().isoformat(),
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
            
            self.optimization_history.append(optimization_record)
            
            return {
                "status": "success" if result.returncode == 0 else "error",
                "task": task.name,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None,
                "timestamp": datetime.now().isoformat()
            }
            
        except subprocess.TimeoutExpired:
            return {
                "status": "timeout",
                "task": task.name,
                "error": "Optimization task timed out"
            }
        except Exception as e:
            return {
                "status": "error",
                "task": task.name,
                "error": str(e)
            }
    
    async def run_full_optimization(self, dry_run: bool = False) -> Dict[str, Any]:
        """Run full system optimization."""
        try:
            print("🐋 Orca OS System Optimizer")
            print("=" * 50)
            
            # Get optimization plan
            tasks = await self.get_optimization_plan()
            
            if not tasks:
                return {"status": "no_tasks", "message": "No optimization tasks recommended"}
            
            print(f"Found {len(tasks)} optimization tasks")
            
            results = []
            successful = 0
            failed = 0
            
            for task in tasks:
                print(f"\nExecuting: {task.name}")
                print(f"Description: {task.description}")
                print(f"AI Recommendation: {task.ai_recommendation}")
                
                result = await self.execute_optimization(task, dry_run)
                results.append(result)
                
                if result["status"] == "success":
                    successful += 1
                    print("✅ Success")
                elif result["status"] == "dry_run":
                    print("🔍 Dry run - would execute")
                else:
                    failed += 1
                    print(f"❌ Failed: {result.get('error', 'Unknown error')}")
            
            return {
                "status": "completed",
                "total_tasks": len(tasks),
                "successful": successful,
                "failed": failed,
                "results": results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}


async def main():
    """Main entry point for Orca Optimizer."""
    optimizer = OrcaOptimizer()
    await optimizer.initialize_optimization_tasks()
    
    # Analyze system
    print("Analyzing system...")
    analysis = await optimizer.analyze_system()
    
    if "error" in analysis:
        print(f"Error: {analysis['error']}")
        return
    
    print(f"System Analysis Complete")
    print(f"Overall Score: {analysis['overall_score']}/100")
    print(f"Memory: {analysis['memory'].get('memory_percent', 0)}%")
    print(f"Disk: {analysis['storage'].get('disk_percent', 0)}%")
    print(f"CPU: {analysis['cpu'].get('cpu_percent', 0)}%")
    
    # Get optimization plan
    tasks = await optimizer.get_optimization_plan()
    print(f"\nRecommended Tasks: {len(tasks)}")
    for task in tasks:
        print(f"  • {task.name}: {task.description} ({task.priority} priority)")


if __name__ == "__main__":
    asyncio.run(main())
