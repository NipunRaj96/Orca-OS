"""
Health Score Engine for Orca OS.
Calculates comprehensive system health score (0-100).
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import psutil

logger = logging.getLogger(__name__)


class HealthScoreEngine:
    """Calculates system health scores."""
    
    def __init__(self):
        """Initialize health score engine."""
        self.weights = {
            'performance': 0.30,  # 30% weight
            'security': 0.25,     # 25% weight
            'stability': 0.25,    # 25% weight
            'efficiency': 0.20    # 20% weight
        }
    
    def calculate_overall_score(self) -> Dict[str, Any]:
        """Calculate overall health score."""
        try:
            # Calculate individual scores
            performance_score = self._calculate_performance_score()
            security_score = self._calculate_security_score()
            stability_score = self._calculate_stability_score()
            efficiency_score = self._calculate_efficiency_score()
            
            # Calculate weighted overall score
            overall_score = (
                performance_score * self.weights['performance'] +
                security_score * self.weights['security'] +
                stability_score * self.weights['stability'] +
                efficiency_score * self.weights['efficiency']
            )
            
            # Determine health status
            if overall_score >= 90:
                status = "excellent"
                status_emoji = "🟢"
            elif overall_score >= 75:
                status = "good"
                status_emoji = "🟡"
            elif overall_score >= 60:
                status = "fair"
                status_emoji = "🟠"
            else:
                status = "poor"
                status_emoji = "🔴"
            
            return {
                'overall_score': round(overall_score, 1),
                'status': status,
                'status_emoji': status_emoji,
                'breakdown': {
                    'performance': {
                        'score': round(performance_score, 1),
                        'weight': self.weights['performance'],
                        'details': self._get_performance_details()
                    },
                    'security': {
                        'score': round(security_score, 1),
                        'weight': self.weights['security'],
                        'details': self._get_security_details()
                    },
                    'stability': {
                        'score': round(stability_score, 1),
                        'weight': self.weights['stability'],
                        'details': self._get_stability_details()
                    },
                    'efficiency': {
                        'score': round(efficiency_score, 1),
                        'weight': self.weights['efficiency'],
                        'details': self._get_efficiency_details()
                    }
                },
                'timestamp': datetime.now().isoformat(),
                'recommendations': self._generate_recommendations(
                    performance_score, security_score, stability_score, efficiency_score
                )
            }
        except Exception as e:
            logger.error(f"Error calculating health score: {e}")
            return {
                'overall_score': 0,
                'status': 'error',
                'error': str(e)
            }
    
    def _calculate_performance_score(self) -> float:
        """Calculate performance score (0-100)."""
        try:
            # CPU performance
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_score = max(0, 100 - (cpu_percent * 1.2))  # Penalize high CPU
            
            # Memory performance
            memory = psutil.virtual_memory()
            mem_score = max(0, 100 - (memory.percent * 1.1))  # Penalize high memory
            
            # Disk I/O (simplified)
            disk = psutil.disk_io_counters()
            disk_score = 85  # Default, can be enhanced with actual I/O metrics
            
            # Average performance score
            performance_score = (cpu_score * 0.4 + mem_score * 0.4 + disk_score * 0.2)
            
            return min(100, max(0, performance_score))
        except Exception as e:
            logger.error(f"Error calculating performance score: {e}")
            return 50.0  # Default score
    
    def _calculate_security_score(self) -> float:
        """Calculate security score (0-100)."""
        try:
            # Basic security checks
            score = 100.0
            
            # Check for running processes (basic security indicator)
            processes = psutil.process_iter(['name'])
            suspicious_processes = []
            
            # Common suspicious process names (basic check)
            suspicious_names = ['keylogger', 'trojan', 'virus']
            for proc in processes:
                try:
                    proc_name = proc.info['name'].lower()
                    if any(sus in proc_name for sus in suspicious_names):
                        suspicious_processes.append(proc_name)
                        score -= 20
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Check system uptime (longer uptime = more stable, but also potential security risk)
            uptime_hours = (datetime.now().timestamp() - psutil.boot_time()) / 3600
            if uptime_hours > 720:  # 30 days
                score -= 5  # Slight penalty for very long uptime (should reboot)
            
            return min(100, max(0, score))
        except Exception as e:
            logger.error(f"Error calculating security score: {e}")
            return 75.0  # Default security score
    
    def _calculate_stability_score(self) -> float:
        """Calculate stability score (0-100)."""
        try:
            score = 100.0
            
            # Check system load
            load_avg = psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 1.0
            cpu_count = psutil.cpu_count()
            
            # Load average should be less than CPU count
            if load_avg > cpu_count * 1.5:
                score -= 30  # High load = instability
            elif load_avg > cpu_count:
                score -= 15
            
            # Check memory pressure
            memory = psutil.virtual_memory()
            if memory.percent > 95:
                score -= 25  # Critical memory = instability
            elif memory.percent > 85:
                score -= 10
            
            # Check swap usage
            swap = psutil.swap_memory()
            if swap.percent > 80:
                score -= 15  # High swap = instability
            
            # Check disk space
            disk = psutil.disk_usage('/')
            if disk.percent > 95:
                score -= 20  # Critical disk = instability
            elif disk.percent > 90:
                score -= 10
            
            return min(100, max(0, score))
        except Exception as e:
            logger.error(f"Error calculating stability score: {e}")
            return 75.0  # Default stability score
    
    def _calculate_efficiency_score(self) -> float:
        """Calculate resource efficiency score (0-100)."""
        try:
            score = 100.0
            
            # CPU efficiency (idle time is good)
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent < 20:
                score += 5  # Bonus for low CPU
            elif cpu_percent > 80:
                score -= 20  # Penalty for high CPU
            
            # Memory efficiency
            memory = psutil.virtual_memory()
            if memory.percent < 50:
                score += 5  # Bonus for low memory usage
            elif memory.percent > 90:
                score -= 25  # Penalty for high memory
            
            # Disk efficiency
            disk = psutil.disk_usage('/')
            if disk.percent < 50:
                score += 5  # Bonus for low disk usage
            elif disk.percent > 90:
                score -= 20  # Penalty for high disk usage
            
            # Process efficiency (fewer processes = more efficient)
            process_count = len(psutil.pids())
            if process_count < 100:
                score += 5
            elif process_count > 300:
                score -= 10
            
            return min(100, max(0, score))
        except Exception as e:
            logger.error(f"Error calculating efficiency score: {e}")
            return 75.0  # Default efficiency score
    
    def _get_performance_details(self) -> Dict[str, Any]:
        """Get performance score details."""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        return {
            'cpu_usage': f"{cpu_percent:.1f}%",
            'memory_usage': f"{memory.percent:.1f}%",
            'cpu_count': psutil.cpu_count()
        }
    
    def _get_security_details(self) -> Dict[str, Any]:
        """Get security score details."""
        uptime_hours = (datetime.now().timestamp() - psutil.boot_time()) / 3600
        
        return {
            'uptime_hours': round(uptime_hours, 1),
            'process_count': len(psutil.pids())
        }
    
    def _get_stability_details(self) -> Dict[str, Any]:
        """Get stability score details."""
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        disk = psutil.disk_usage('/')
        
        try:
            load_avg = psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0.0
        except:
            load_avg = 0.0
        
        return {
            'memory_percent': f"{memory.percent:.1f}%",
            'swap_percent': f"{swap.percent:.1f}%",
            'disk_percent': f"{disk.percent:.1f}%",
            'load_average': round(load_avg, 2)
        }
    
    def _get_efficiency_details(self) -> Dict[str, Any]:
        """Get efficiency score details."""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        process_count = len(psutil.pids())
        
        return {
            'cpu_usage': f"{cpu_percent:.1f}%",
            'memory_usage': f"{memory.percent:.1f}%",
            'disk_usage': f"{disk.percent:.1f}%",
            'process_count': process_count
        }
    
    def _generate_recommendations(
        self,
        performance: float,
        security: float,
        stability: float,
        efficiency: float
    ) -> List[str]:
        """Generate recommendations based on scores."""
        recommendations = []
        
        if performance < 70:
            recommendations.append("Performance is below optimal - consider optimizing processes")
        
        if security < 80:
            recommendations.append("Security score is low - review system security")
        
        if stability < 70:
            recommendations.append("System stability needs attention - check resource usage")
        
        if efficiency < 70:
            recommendations.append("Resource efficiency can be improved - optimize resource usage")
        
        if not recommendations:
            recommendations.append("System is in good health - keep monitoring")
        
        return recommendations

