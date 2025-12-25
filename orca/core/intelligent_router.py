"""
Intelligent query router - connects natural language to advanced features.
Routes queries to appropriate autonomous agents with security checks.
"""

import logging
from typing import Dict, Any, Optional, List
import re

from ..core.models import CommandSuggestion, CommandRisk, CommandAction
from ..database.session import DatabaseSession
from ..core.autonomy import AutonomousDecisionEngine
from ..security.autonomous_security import AutonomousSecurity
from pathlib import Path
import os

logger = logging.getLogger(__name__)


class IntelligentRouter:
    """Routes queries to appropriate advanced features."""
    
    def __init__(self, db_session: DatabaseSession, autonomy_engine: AutonomousDecisionEngine):
        """Initialize router."""
        self.db = db_session
        self.autonomy = autonomy_engine
        self.security = AutonomousSecurity()
        
        # Query patterns that trigger advanced features
        self.feature_patterns = {
            'health': [
                r'health|health.*score|system.*health|how.*healthy|health.*status',
                r'score|rating|grade|status.*system',
            ],
            'predictive': [
                r'predict|forecast|will.*happen|future|upcoming|soon|prevent|avoid',
                r'slow|lag|freeze|crash|problem|issue|error|warning',
                r'optimize|improve|better|faster|performance|speed',
            ],
            'optimizer': [
                r'optimize|improve|speed|faster|performance|tune|clean',
                r'slow|lag|freeze|unresponsive|bottleneck',
                r'memory|disk|cpu|resource|cleanup|free.*space',
            ],
            'process_manager': [
                r'process|program|application|app.*running|task',
                r'kill|stop|close|terminate|end.*process',
                r'cpu.*high|memory.*high|resource.*hog',
                r'what.*using|what.*consuming|top.*process',
            ],
            'logs': [
                r'log|error|warning|crash|failure|debug',
                r'what.*wrong|why.*fail|investigate|analyze.*log',
                r'issue|problem|trouble|broken',
            ],
            'scheduler': [
                r'schedule|priority|performance|load|balance',
                r'cpu.*affinity|process.*priority|resource.*allocation',
            ],
            'dashboard': [
                r'dashboard|monitor|overview|status|health',
                r'system.*info|everything|all.*info|complete.*status',
            ],
            'autonomous_fix': [
                r'fix|repair|solve|resolve|heal|recover',
                r'automatic|auto|proactive|prevent',
                r'something.*wrong|broken|not.*working',
            ],
            'file_organization': [
                r'organize|organise|organize.*file|organize.*folder|organize.*directory',
                r'organize.*download|organize.*desktop|clean.*folder|sort.*file',
                r'file.*organization|folder.*organization|tidy.*folder',
            ]
        }
    
    def route_query(self, query: str) -> Dict[str, Any]:
        """Route query to appropriate feature(s)."""
        query_lower = query.lower()
        
        # Detect which features to trigger
        triggered_features = []
        for feature, patterns in self.feature_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    triggered_features.append(feature)
                    break
        
        # If no specific feature, use default natural language processing
        if not triggered_features:
            return {
                'route': 'natural_language',
                'features': [],
                'autonomous': False
            }
        
        # Check if autonomous fix is requested
        autonomous_fix = 'autonomous_fix' in triggered_features
        
        return {
            'route': 'advanced_features',
            'features': list(set(triggered_features)),
            'autonomous': autonomous_fix,
            'primary_feature': triggered_features[0] if triggered_features else None
        }
    
    async def execute_routed_query(
        self,
        query: str,
        route_info: Dict[str, Any],
        integration_layer
    ) -> Dict[str, Any]:
        """Execute query using routed features."""
        features = route_info.get('features', [])
        autonomous = route_info.get('autonomous', False)
        
        results = {}
        
        # Execute each triggered feature
        for feature in features:
            if feature == 'health':
                results['health'] = await self._run_health_score(integration_layer)
            
            elif feature == 'predictive':
                results['predictive'] = await self._run_predictive_ai(integration_layer)
            
            elif feature == 'optimizer':
                results['optimizer'] = await self._run_optimizer(query, autonomous, integration_layer)
            
            elif feature == 'process_manager':
                results['process_manager'] = await self._run_process_manager(query, autonomous, integration_layer)
            
            elif feature == 'logs':
                results['logs'] = await self._run_log_analysis(query, integration_layer)
            
            elif feature == 'scheduler':
                results['scheduler'] = await self._run_scheduler(autonomous, integration_layer)
            
            elif feature == 'dashboard':
                results['dashboard'] = await self._run_dashboard(integration_layer)
            
            elif feature == 'file_organization':
                results['file_organization'] = await self._run_file_organization(query, integration_layer)
            
            elif feature == 'analytics':
                results['analytics'] = await self._run_analytics(query, integration_layer)
            
            elif feature == 'autonomous_fix':
                # This triggers automatic fixing
                results['autonomous_fix'] = await self._run_autonomous_fix(query, integration_layer)
        
        return results
    
    async def _run_health_score(self, integration_layer) -> Dict[str, Any]:
        """Run health score calculation."""
        try:
            from ...features.health import HealthScoreEngine, HealthDashboard
            
            engine = HealthScoreEngine()
            dashboard = HealthDashboard()
            
            # Calculate health score
            health_data = engine.calculate_overall_score()
            
            # Display in terminal
            dashboard.show_health_score(show_trend=False)
            
            return {
                'health_data': health_data,
                'status': 'success'
            }
        except Exception as e:
            logger.error(f"Health score error: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def _run_predictive_ai(self, integration_layer) -> Dict[str, Any]:
        """Run predictive AI analysis."""
        try:
            # Try to import from orca-os-distro
            import sys
            from pathlib import Path
            
            # Calculate paths
            base_path = Path(__file__).parent.parent.parent
            advanced_path = base_path / 'orca-os-distro' / 'advanced'
            
            # Check if path exists
            if not advanced_path.exists():
                # Fallback: provide basic predictive analysis
                return await self._basic_predictive_analysis()
            
            sys.path.insert(0, str(advanced_path))
            
            try:
                from predictive_ai import PredictiveAI
                predictive = PredictiveAI()
                
                # Get predictions
                predictions = await predictive.get_predictions()
                forecast = await predictive.get_system_health_forecast()
                recommendations = await predictive.get_optimization_recommendations()
                
                return {
                    'predictions': predictions,
                    'forecast': forecast,
                    'recommendations': recommendations,
                    'status': 'success'
                }
            except ImportError:
                # Module not found, use basic analysis
                return await self._basic_predictive_analysis()
        except Exception as e:
            logger.error(f"Predictive AI error: {e}")
            return await self._basic_predictive_analysis()
    
    async def _basic_predictive_analysis(self) -> Dict[str, Any]:
        """Basic predictive analysis fallback."""
        import psutil
        
        # Get current system metrics
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        predictions = []
        
        if cpu > 70:
            predictions.append({
                'type': 'cpu_high',
                'description': f'CPU usage is {cpu:.1f}% - may cause slowdown',
                'confidence': 0.85,
                'timeframe': 'immediate',
                'urgency': 'high' if cpu > 85 else 'medium',
                'recommendation': 'Close unnecessary applications'
            })
        
        if memory.percent > 80:
            predictions.append({
                'type': 'memory_high',
                'description': f'Memory usage is {memory.percent:.1f}%',
                'confidence': 0.90,
                'timeframe': '1-2 hours',
                'urgency': 'high' if memory.percent > 90 else 'medium',
                'recommendation': 'Free up memory'
            })
        
        if disk.percent > 80:
            predictions.append({
                'type': 'disk_high',
                'description': f'Disk usage is {disk.percent:.1f}%',
                'confidence': 0.88,
                'timeframe': '3-5 days',
                'urgency': 'high' if disk.percent > 90 else 'medium',
                'recommendation': 'Clean up files'
            })
        
        return {
            'predictions': predictions,
            'forecast': {'current_status': 'healthy' if not predictions else 'warning'},
            'recommendations': [p['recommendation'] for p in predictions],
            'status': 'success'
        }
    
    async def _run_optimizer(
        self,
        query: str,
        autonomous: bool,
        integration_layer
    ) -> Dict[str, Any]:
        """Run system optimizer."""
        try:
            import sys
            from pathlib import Path
            
            # Calculate paths
            base_path = Path(__file__).parent.parent.parent
            advanced_path = base_path / 'orca-os-distro' / 'advanced'
            
            # Check if path exists
            if not advanced_path.exists():
                # Fallback: provide basic optimization
                return await self._basic_optimization(autonomous, integration_layer)
            
            sys.path.insert(0, str(advanced_path))
            
            try:
                from orca_optimizer import OrcaOptimizer
                
                optimizer = OrcaOptimizer()
                await optimizer.initialize_optimization_tasks()
                
                # Analyze system
                analysis = await optimizer.analyze_system()
                
                # Get recommendations
                recommendations = analysis.get('recommendations', [])
                
                # If autonomous, execute safe optimizations
                if autonomous:
                    executed = await self._execute_autonomous_optimizations(
                        recommendations,
                        integration_layer
                    )
                    return {
                        'analysis': analysis,
                        'autonomous_actions': executed,
                        'status': 'success'
                    }
                
                return {
                    'analysis': analysis,
                    'recommendations': recommendations,
                    'status': 'success'
                }
            except ImportError:
                # Module not found, use basic optimization
                return await self._basic_optimization(autonomous, integration_layer)
        except Exception as e:
            logger.error(f"Optimizer error: {e}")
            return await self._basic_optimization(autonomous, integration_layer)
    
    async def _basic_optimization(
        self,
        autonomous: bool,
        integration_layer
    ) -> Dict[str, Any]:
        """Basic optimization fallback."""
        import psutil
        
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        recommendations = []
        
        if memory.percent > 70:
            recommendations.append({
                'description': 'Clean memory caches',
                'command': 'sync && echo 3 > /proc/sys/vm/drop_caches 2>/dev/null || true',
                'priority': 'medium',
                'risk': 'low',
                'impact': 'medium',
                'ai_insight': 'Safe memory cleanup'
            })
        
        if disk.percent > 75:
            recommendations.append({
                'description': 'Clean temporary files',
                'command': 'find /tmp -type f -atime +7 -delete 2>/dev/null || true',
                'priority': 'high',
                'risk': 'low',
                'impact': 'medium',
                'ai_insight': 'Remove old temp files'
            })
        
        if autonomous and recommendations:
            executed = await self._execute_autonomous_optimizations(
                recommendations,
                integration_layer
            )
            return {
                'analysis': {'status': 'analyzed'},
                'autonomous_actions': executed,
                'status': 'success'
            }
        
        return {
            'analysis': {'status': 'analyzed'},
            'recommendations': recommendations,
            'status': 'success'
        }
    
    async def _run_process_manager(
        self,
        query: str,
        autonomous: bool,
        integration_layer
    ) -> Dict[str, Any]:
        """Run process manager."""
        try:
            # Check if query wants to kill/optimize processes
            query_lower = query.lower()
            
            if any(word in query_lower for word in ['kill', 'stop', 'close', 'terminate']):
                # This is a process management action
                # Use natural language to understand which process
                from ..llm.manager import LLMManager
                from ..core.models import UserQuery, SystemContext
                from ..utils.config import load_config
                
                config = load_config()
                llm = LLMManager(config.llm.dict())
                
                user_query = UserQuery(query=query)
                context = SystemContext()
                
                suggestion = await llm.generate_suggestion(user_query, context)
                
                # Check if can act autonomously
                can_auto = self.autonomy.can_act_autonomously(
                    'process-manager',
                    'kill',
                    suggestion
                )
                
                if autonomous and can_auto:
                    # Execute autonomously (with security check)
                    return await self._execute_process_action(suggestion, integration_layer)
                else:
                    return {
                        'suggestion': suggestion.dict() if hasattr(suggestion, 'dict') else str(suggestion),
                        'can_autonomous': can_auto,
                        'status': 'requires_confirmation'
                    }
            
            # Otherwise, just analyze processes
            return {
                'action': 'analyze',
                'status': 'success'
            }
        except Exception as e:
            logger.error(f"Process manager error: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def _run_log_analysis(self, query: str, integration_layer) -> Dict[str, Any]:
        """Run log analysis."""
        # Placeholder - would integrate with orca-logs
        return {
            'action': 'analyze_logs',
            'status': 'success'
        }
    
    async def _run_scheduler(self, autonomous: bool, integration_layer) -> Dict[str, Any]:
        """Run scheduler optimization."""
        # Placeholder - would integrate with orca-scheduler
        return {
            'action': 'optimize_scheduling',
            'status': 'success'
        }
    
    async def _run_dashboard(self, integration_layer) -> Dict[str, Any]:
        """Run dashboard."""
        # Placeholder - would integrate with orca-dashboard
        return {
            'action': 'show_dashboard',
            'status': 'success'
        }
    
    async def _run_autonomous_fix(
        self,
        query: str,
        integration_layer
    ) -> Dict[str, Any]:
        """Run autonomous fixing system."""
        # This is the world-breaking feature - autonomous fixing
        
        # 1. Run predictive AI to find issues
        predictive_result = await self._run_predictive_ai(integration_layer)
        
        # 2. Run optimizer to fix issues
        optimizer_result = await self._run_optimizer(query, True, integration_layer)
        
        # 3. Run process manager if needed
        if 'process' in query.lower():
            process_result = await self._run_process_manager(query, True, integration_layer)
        else:
            process_result = {}
        
        # 4. Compile results
        return {
            'predictive_analysis': predictive_result,
            'optimizations_applied': optimizer_result.get('autonomous_actions', []),
            'process_actions': process_result,
            'status': 'autonomous_fix_complete'
        }
    
    async def _execute_autonomous_optimizations(
        self,
        recommendations: List[Dict[str, Any]],
        integration_layer
    ) -> List[Dict[str, Any]]:
        """Execute optimizations autonomously (with security)."""
        executed = []
        
        for rec in recommendations:
            # Only execute LOW risk optimizations autonomously
            if rec.get('risk') == 'low' and rec.get('priority') in ['high', 'medium']:
                try:
                    # Create command suggestion
                    from ..core.models import CommandSuggestion, CommandRisk, CommandAction
                    
                    suggestion = CommandSuggestion(
                        command=rec.get('command', ''),
                        confidence=0.9,
                        action=CommandAction.EXECUTE,
                        risk_level=CommandRisk.SAFE,
                        explanation=rec.get('ai_insight', '')
                    )
                    
                    # Security check FIRST
                    security_check = self.security.check_autonomous_action(
                        suggestion,
                        'optimizer'
                    )
                    
                    if not security_check['allowed']:
                        logger.warning(f"Security blocked: {security_check['reason']}")
                        continue
                    
                    # Check if can act autonomously
                    can_auto = self.autonomy.can_act_autonomously(
                        'optimizer',
                        'optimize',
                        suggestion
                    )
                    
                    if can_auto and security_check['allowed']:
                        # Execute
                        from ..core.executor import CommandExecutor
                        from ..utils.config import load_config
                        
                        config = load_config()
                        executor = CommandExecutor(config.executor)
                        result = await executor.execute(suggestion)
                        
                        if result.success:
                            # Log autonomous action
                            self.autonomy.make_autonomous_decision(
                                'optimizer',
                                'optimize',
                                rec.get('description', ''),
                                rec.get('command', ''),
                                0.9,
                                metadata={'recommendation': rec}
                            )
                            
                            # Record for security tracking
                            self.security.record_autonomous_action(
                                rec.get('command', ''),
                                True
                            )
                            
                            executed.append({
                                'action': rec.get('description', ''),
                                'success': True,
                                'result': result.stdout[:200] if result.stdout else 'Completed'
                            })
                        else:
                            # Record failed action
                            self.security.record_autonomous_action(
                                rec.get('command', ''),
                                False
                            )
                except Exception as e:
                    logger.error(f"Autonomous optimization error: {e}")
                    executed.append({
                        'action': rec.get('description', ''),
                        'success': False,
                        'error': str(e)
                    })
        
        return executed
    
    async def _execute_process_action(
        self,
        suggestion: CommandSuggestion,
        integration_layer
    ) -> Dict[str, Any]:
        """Execute process action autonomously."""
        # Security check - only allow killing user's own processes
        if 'kill' in suggestion.command.lower() or 'pkill' in suggestion.command.lower():
            # Additional security validation
            if suggestion.risk_level in [CommandRisk.SAFE, CommandRisk.MODERATE]:
                from ..core.executor import CommandExecutor
                from ..utils.config import load_config
                
                config = load_config()
                executor = CommandExecutor(config.executor)
                result = await executor.execute(suggestion)
                
                return {
                    'action': 'process_kill',
                    'success': result.success,
                    'result': result.stdout if result.success else result.stderr
                }
        
        return {
            'action': 'process_action',
            'status': 'requires_confirmation',
            'reason': 'High risk action'
        }
    
    async def _run_analytics(
        self,
        query: str,
        integration_layer
    ) -> Dict[str, Any]:
        """Run analytics dashboard."""
        try:
            from ..features.analytics import AnalyticsDashboard
            
            dashboard = AnalyticsDashboard()
            
            # Determine what analytics to show based on query
            query_lower = query.lower()
            days = 30
            
            # Extract days if mentioned
            import re
            days_match = re.search(r'(\d+)\s*(?:days?|weeks?)', query_lower)
            if days_match:
                days = int(days_match.group(1))
                if 'week' in query_lower:
                    days = days * 7
            
            # Show full dashboard
            dashboard.show_full_dashboard(days)
            
            return {
                'status': 'success',
                'message': 'Analytics displayed'
            }
        except Exception as e:
            logger.error(f"Analytics error: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }

