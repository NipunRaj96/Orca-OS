"""
Aggressive self-healing system for Orca OS.
Proactive issue detection and automatic fix application.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import psutil

from ...core.autonomy import AutonomousDecisionEngine
from ...security.autonomous_security import AutonomousSecurity
from ...database.session import DatabaseSession
from ...database.init_db import initialize_database

logger = logging.getLogger(__name__)


class AggressiveSelfHealing:
    """Enhanced self-healing system with proactive issue detection."""
    
    def __init__(self, autonomy_engine: AutonomousDecisionEngine):
        """Initialize self-healing system."""
        initialize_database()
        self.db = DatabaseSession()
        self.autonomy = autonomy_engine
        self.security = AutonomousSecurity()
        self.healing_history = []
    
    async def detect_issues(self) -> List[Dict[str, Any]]:
        """Proactively detect system issues."""
        issues = []
        
        try:
            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 85:
                issues.append({
                    'type': 'high_cpu',
                    'severity': 'high',
                    'description': f'CPU usage is {cpu_percent:.1f}% (critical)',
                    'metric': cpu_percent,
                    'threshold': 85
                })
            elif cpu_percent > 70:
                issues.append({
                    'type': 'high_cpu',
                    'severity': 'medium',
                    'description': f'CPU usage is {cpu_percent:.1f}% (elevated)',
                    'metric': cpu_percent,
                    'threshold': 70
                })
            
            # Check memory usage
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                issues.append({
                    'type': 'high_memory',
                    'severity': 'high',
                    'description': f'Memory usage is {memory.percent:.1f}% (critical)',
                    'metric': memory.percent,
                    'threshold': 90
                })
            elif memory.percent > 80:
                issues.append({
                    'type': 'high_memory',
                    'severity': 'medium',
                    'description': f'Memory usage is {memory.percent:.1f}% (elevated)',
                    'metric': memory.percent,
                    'threshold': 80
                })
            
            # Check disk usage
            disk = psutil.disk_usage('/')
            if disk.percent > 90:
                issues.append({
                    'type': 'high_disk',
                    'severity': 'high',
                    'description': f'Disk usage is {disk.percent:.1f}% (critical)',
                    'metric': disk.percent,
                    'threshold': 90
                })
            elif disk.percent > 80:
                issues.append({
                    'type': 'high_disk',
                    'severity': 'medium',
                    'description': f'Disk usage is {disk.percent:.1f}% (elevated)',
                    'metric': disk.percent,
                    'threshold': 80
                })
            
            # Check for zombie processes
            processes = psutil.process_iter(['pid', 'status'])
            zombie_count = sum(1 for p in processes if p.info['status'] == psutil.STATUS_ZOMBIE)
            if zombie_count > 5:
                issues.append({
                    'type': 'zombie_processes',
                    'severity': 'medium',
                    'description': f'Found {zombie_count} zombie processes',
                    'metric': zombie_count,
                    'threshold': 5
                })
            
            # Check for high-load processes
            top_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    proc.info['cpu_percent'] = proc.cpu_percent(interval=0.1)
                    if proc.info['cpu_percent'] > 50 or proc.info['memory_percent'] > 20:
                        top_processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            if len(top_processes) > 0:
                # Sort by CPU usage
                top_processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
                top_proc = top_processes[0]
                if top_proc.get('cpu_percent', 0) > 80:
                    issues.append({
                        'type': 'resource_hog',
                        'severity': 'high',
                        'description': f"Process '{top_proc.get('name', 'unknown')}' using {top_proc.get('cpu_percent', 0):.1f}% CPU",
                        'metric': top_proc.get('cpu_percent', 0),
                        'process': top_proc
                    })
        
        except Exception as e:
            logger.error(f"Error detecting issues: {e}")
        
        return issues
    
    async def apply_fixes(self, issues: List[Dict[str, Any]], autonomous: bool = True) -> List[Dict[str, Any]]:
        """Apply fixes for detected issues."""
        fixes_applied = []
        
        for issue in issues:
            try:
                fix_result = await self._fix_issue(issue, autonomous)
                if fix_result:
                    fixes_applied.append({
                        'issue': issue,
                        'fix': fix_result,
                        'timestamp': datetime.now().isoformat()
                    })
                    self.healing_history.append({
                        'issue': issue,
                        'fix': fix_result,
                        'timestamp': datetime.now()
                    })
            except Exception as e:
                logger.error(f"Error applying fix for {issue.get('type')}: {e}")
                fixes_applied.append({
                    'issue': issue,
                    'fix': {'success': False, 'error': str(e)},
                    'timestamp': datetime.now().isoformat()
                })
        
        return fixes_applied
    
    async def _fix_issue(self, issue: Dict[str, Any], autonomous: bool) -> Optional[Dict[str, Any]]:
        """Fix a specific issue."""
        issue_type = issue.get('type')
        severity = issue.get('severity')
        
        # Only fix medium/high severity issues autonomously
        if severity not in ['medium', 'high']:
            return None
        
        # Check if we can act autonomously
        if not autonomous:
            return {
                'success': False,
                'reason': 'Autonomous mode disabled',
                'action_required': self._get_fix_suggestion(issue)
            }
        
        try:
            if issue_type == 'high_cpu':
                return await self._fix_high_cpu(issue)
            elif issue_type == 'high_memory':
                return await self._fix_high_memory(issue)
            elif issue_type == 'high_disk':
                return await self._fix_high_disk(issue)
            elif issue_type == 'zombie_processes':
                return await self._fix_zombie_processes(issue)
            elif issue_type == 'resource_hog':
                return await self._fix_resource_hog(issue)
        except Exception as e:
            logger.error(f"Error fixing {issue_type}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
        
        return None
    
    async def _fix_high_cpu(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Fix high CPU usage."""
        # Find and kill resource-intensive processes (user's own processes only)
        try:
            import subprocess
            
            # Get top CPU-consuming processes
            result = subprocess.run(
                ['ps', 'aux', '--sort=-%cpu', '--no-headers'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[:5]  # Top 5
                killed = []
                
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 11:
                        pid = parts[1]
                        cpu = float(parts[2])
                        user = parts[0]
                        
                        # Only kill user's own processes with very high CPU
                        if cpu > 80 and user == psutil.Process().username():
                            try:
                                proc = psutil.Process(int(pid))
                                proc.terminate()
                                killed.append({'pid': pid, 'cpu': cpu})
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                pass
                
                if killed:
                    return {
                        'success': True,
                        'action': 'terminated_high_cpu_processes',
                        'processes_killed': len(killed),
                        'details': killed
                    }
            
            return {
                'success': True,
                'action': 'analyzed_cpu_usage',
                'message': 'CPU usage monitored, no immediate action needed'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _fix_high_memory(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Fix high memory usage."""
        try:
            # Clear system caches if possible (Linux)
            import platform
            if platform.system() == 'Linux':
                import subprocess
                # Try to clear page cache (requires root, so may fail)
                result = subprocess.run(
                    ['sudo', 'sync', '&&', 'sudo', 'sysctl', '-w', 'vm.drop_caches=1'],
                    capture_output=True,
                    timeout=10,
                    shell=True
                )
                
                if result.returncode == 0:
                    return {
                        'success': True,
                        'action': 'cleared_system_cache',
                        'message': 'System cache cleared'
                    }
            
            return {
                'success': True,
                'action': 'monitored_memory',
                'message': 'Memory usage monitored, consider closing applications'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _fix_high_disk(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Fix high disk usage."""
        return {
            'success': True,
            'action': 'monitored_disk',
            'message': 'Disk usage monitored, consider cleaning up files',
            'suggestion': 'Use file organization feature to clean up'
        }
    
    async def _fix_zombie_processes(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Fix zombie processes."""
        # Zombie processes are usually cleaned up by init
        # We can't directly kill them, but we can report them
        return {
            'success': True,
            'action': 'monitored_zombies',
            'message': 'Zombie processes detected, system will clean them up automatically'
        }
    
    async def _fix_resource_hog(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Fix resource-hogging process."""
        process_info = issue.get('process', {})
        pid = process_info.get('pid')
        
        if not pid:
            return {
                'success': False,
                'error': 'Process ID not available'
            }
        
        try:
            proc = psutil.Process(pid)
            # Only kill if it's the user's own process
            if proc.username() == psutil.Process().username():
                proc.terminate()
                # Wait a bit, then force kill if needed
                await asyncio.sleep(2)
                try:
                    proc.kill()
                except psutil.NoSuchProcess:
                    pass
                
                return {
                    'success': True,
                    'action': 'terminated_resource_hog',
                    'pid': pid,
                    'process_name': process_info.get('name', 'unknown')
                }
            else:
                return {
                    'success': False,
                    'reason': 'Cannot terminate system process',
                    'suggestion': 'Contact system administrator'
                }
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_fix_suggestion(self, issue: Dict[str, Any]) -> str:
        """Get human-readable fix suggestion."""
        issue_type = issue.get('type')
        suggestions = {
            'high_cpu': 'Close unnecessary applications or restart resource-intensive processes',
            'high_memory': 'Close applications to free up memory',
            'high_disk': 'Delete unnecessary files or use file organization feature',
            'zombie_processes': 'System will clean up automatically, or restart if persistent',
            'resource_hog': 'Close the resource-intensive application'
        }
        return suggestions.get(issue_type, 'Review system resources')
    
    async def verify_healing(self, fixes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Verify that fixes were successful."""
        verification_results = []
        
        for fix_data in fixes:
            issue = fix_data.get('issue', {})
            fix = fix_data.get('fix', {})
            
            if fix.get('success'):
                # Re-check the issue
                await asyncio.sleep(2)  # Wait for system to stabilize
                
                # Re-detect issues
                current_issues = await self.detect_issues()
                issue_type = issue.get('type')
                
                # Check if the same issue still exists
                still_exists = any(
                    i.get('type') == issue_type 
                    for i in current_issues
                )
                
                verification_results.append({
                    'issue_type': issue_type,
                    'fix_applied': True,
                    'issue_resolved': not still_exists,
                    'timestamp': datetime.now().isoformat()
                })
            else:
                verification_results.append({
                    'issue_type': issue.get('type'),
                    'fix_applied': False,
                    'issue_resolved': False,
                    'error': fix.get('error', 'Unknown error')
                })
        
        return {
            'verification_results': verification_results,
            'total_fixes': len(fixes),
            'successful_fixes': sum(1 for r in verification_results if r.get('fix_applied')),
            'resolved_issues': sum(1 for r in verification_results if r.get('issue_resolved'))
        }
    
    async def run_healing_cycle(self, autonomous: bool = True) -> Dict[str, Any]:
        """Run a complete healing cycle: detect, fix, verify."""
        # Detect issues
        issues = await self.detect_issues()
        
        if not issues:
            return {
                'status': 'no_issues',
                'message': 'No issues detected',
                'timestamp': datetime.now().isoformat()
            }
        
        # Apply fixes
        fixes = await self.apply_fixes(issues, autonomous)
        
        # Verify healing
        verification = await self.verify_healing(fixes)
        
        return {
            'status': 'healing_complete',
            'issues_detected': len(issues),
            'fixes_applied': len(fixes),
            'verification': verification,
            'timestamp': datetime.now().isoformat()
        }

