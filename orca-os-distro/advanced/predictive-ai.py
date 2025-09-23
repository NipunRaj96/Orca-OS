#!/usr/bin/env python3
"""
Orca Predictive AI Assistant
Predictive system monitoring and intelligent recommendations
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
class Prediction:
    """System prediction with confidence and recommendations."""
    type: str
    description: str
    confidence: float
    timeframe: str
    impact: str
    recommendation: str
    urgency: str


@dataclass
class SystemTrend:
    """System trend analysis."""
    metric: str
    current_value: float
    trend: str
    change_rate: float
    prediction: str


class PredictiveAI:
    """Predictive AI assistant for Orca OS."""
    
    def __init__(self):
        """Initialize the predictive AI."""
        self.config = load_config('/opt/orca-os/config/orca.yaml')
        self.llm_manager = LLMManager(self.config.llm.dict())
        self.history = []
        self.predictions = []
        self.monitoring_active = False
        
        # Prediction thresholds
        self.cpu_threshold = 80.0
        self.memory_threshold = 85.0
        self.disk_threshold = 90.0
        self.temperature_threshold = 80.0
        
    async def start_monitoring(self, interval: int = 60):
        """Start predictive monitoring."""
        self.monitoring_active = True
        
        while self.monitoring_active:
            try:
                # Collect system metrics
                metrics = await self._collect_system_metrics()
                self.history.append(metrics)
                
                # Keep only last 24 hours of data
                cutoff_time = datetime.now() - timedelta(hours=24)
                self.history = [m for m in self.history if m['timestamp'] > cutoff_time]
                
                # Generate predictions
                predictions = await self._generate_predictions()
                self.predictions.extend(predictions)
                
                # Keep only recent predictions
                self.predictions = self.predictions[-100:]  # Keep last 100 predictions
                
                # Wait for next interval
                await asyncio.sleep(interval)
                
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                await asyncio.sleep(interval)
    
    def stop_monitoring(self):
        """Stop predictive monitoring."""
        self.monitoring_active = False
    
    async def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect current system metrics."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_freq = psutil.cpu_freq()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            
            # Network metrics
            network = psutil.net_io_counters()
            
            # Process metrics
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    proc_info = proc.info
                    if proc_info['cpu_percent'] and proc_info['cpu_percent'] > 1.0:
                        processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Temperature (if available)
            try:
                temps = psutil.sensors_temperatures()
                cpu_temp = None
                if 'coretemp' in temps:
                    cpu_temp = temps['coretemp'][0].current
            except:
                cpu_temp = None
            
            return {
                "timestamp": datetime.now().isoformat(),
                "cpu": {
                    "percent": cpu_percent,
                    "frequency": cpu_freq.current if cpu_freq else None,
                    "count": psutil.cpu_count()
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
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                },
                "processes": {
                    "count": len(processes),
                    "top_cpu": sorted(processes, key=lambda x: x['cpu_percent'] or 0, reverse=True)[:5]
                },
                "temperature": {
                    "cpu": cpu_temp
                }
            }
            
        except Exception as e:
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    async def _generate_predictions(self) -> List[Prediction]:
        """Generate predictions based on current data."""
        predictions = []
        
        try:
            if len(self.history) < 5:  # Need at least 5 data points
                return predictions
            
            # Analyze trends
            trends = await self._analyze_trends()
            
            # Generate predictions for each trend
            for trend in trends:
                prediction = await self._create_prediction(trend)
                if prediction:
                    predictions.append(prediction)
            
            # Check for immediate issues
            immediate_predictions = await self._check_immediate_issues()
            predictions.extend(immediate_predictions)
            
        except Exception as e:
            print(f"Error generating predictions: {e}")
        
        return predictions
    
    async def _analyze_trends(self) -> List[SystemTrend]:
        """Analyze system trends."""
        trends = []
        
        try:
            if len(self.history) < 3:
                return trends
            
            # Get recent data points
            recent_data = self.history[-10:]  # Last 10 data points
            
            # Analyze CPU trend
            cpu_values = [d['cpu']['percent'] for d in recent_data if 'cpu' in d]
            if len(cpu_values) >= 3:
                trend = self._calculate_trend(cpu_values)
                trends.append(SystemTrend(
                    metric="CPU Usage",
                    current_value=cpu_values[-1],
                    trend=trend['direction'],
                    change_rate=trend['rate'],
                    prediction=trend['prediction']
                ))
            
            # Analyze memory trend
            memory_values = [d['memory']['percent'] for d in recent_data if 'memory' in d]
            if len(memory_values) >= 3:
                trend = self._calculate_trend(memory_values)
                trends.append(SystemTrend(
                    metric="Memory Usage",
                    current_value=memory_values[-1],
                    trend=trend['direction'],
                    change_rate=trend['rate'],
                    prediction=trend['prediction']
                ))
            
            # Analyze disk trend
            disk_values = [d['disk']['percent'] for d in recent_data if 'disk' in d]
            if len(disk_values) >= 3:
                trend = self._calculate_trend(disk_values)
                trends.append(SystemTrend(
                    metric="Disk Usage",
                    current_value=disk_values[-1],
                    trend=trend['direction'],
                    change_rate=trend['rate'],
                    prediction=trend['prediction']
                ))
            
        except Exception as e:
            print(f"Error analyzing trends: {e}")
        
        return trends
    
    def _calculate_trend(self, values: List[float]) -> Dict[str, Any]:
        """Calculate trend from a series of values."""
        try:
            if len(values) < 3:
                return {"direction": "stable", "rate": 0, "prediction": "insufficient_data"}
            
            # Simple linear regression
            n = len(values)
            x = list(range(n))
            y = values
            
            # Calculate slope
            x_mean = sum(x) / n
            y_mean = sum(y) / n
            
            numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
            denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
            
            if denominator == 0:
                slope = 0
            else:
                slope = numerator / denominator
            
            # Determine trend direction
            if slope > 0.5:
                direction = "increasing"
            elif slope < -0.5:
                direction = "decreasing"
            else:
                direction = "stable"
            
            # Predict future value
            future_value = y[-1] + slope * 5  # Predict 5 time units ahead
            
            return {
                "direction": direction,
                "rate": slope,
                "prediction": f"Expected to reach {future_value:.1f}% in 5 time units"
            }
            
        except Exception as e:
            return {"direction": "unknown", "rate": 0, "prediction": f"Error: {e}"}
    
    async def _create_prediction(self, trend: SystemTrend) -> Optional[Prediction]:
        """Create a prediction from a trend."""
        try:
            # Determine if trend is concerning
            concerning = False
            urgency = "low"
            impact = "minimal"
            
            if trend.metric == "CPU Usage":
                if trend.current_value > self.cpu_threshold or trend.change_rate > 2:
                    concerning = True
                    urgency = "high" if trend.current_value > 90 else "medium"
                    impact = "high" if trend.current_value > 90 else "medium"
            elif trend.metric == "Memory Usage":
                if trend.current_value > self.memory_threshold or trend.change_rate > 1:
                    concerning = True
                    urgency = "high" if trend.current_value > 95 else "medium"
                    impact = "high" if trend.current_value > 95 else "medium"
            elif trend.metric == "Disk Usage":
                if trend.current_value > self.disk_threshold or trend.change_rate > 0.5:
                    concerning = True
                    urgency = "high" if trend.current_value > 95 else "medium"
                    impact = "high" if trend.current_value > 95 else "medium"
            
            if not concerning:
                return None
            
            # Generate AI recommendation
            context = f"""
            Metric: {trend.metric}
            Current Value: {trend.current_value}%
            Trend: {trend.trend}
            Change Rate: {trend.change_rate}
            Prediction: {trend.prediction}
            """
            
            query = UserQuery(query=f"Provide a recommendation for this system trend: {context}")
            system_context = SystemContext(
                processes=[],
                memory_usage=trend.current_value if trend.metric == "Memory Usage" else 0,
                cpu_usage=trend.current_value if trend.metric == "CPU Usage" else 0,
                disk_usage=trend.current_value if trend.metric == "Disk Usage" else 0
            )
            
            suggestion = await self.llm_manager.generate_suggestion(query, system_context)
            
            return Prediction(
                type=trend.metric.lower().replace(" ", "_"),
                description=f"{trend.metric} is {trend.trend} and may reach critical levels",
                confidence=min(0.9, abs(trend.change_rate) * 0.1 + 0.5),
                timeframe="1-2 hours" if urgency == "high" else "4-6 hours",
                impact=impact,
                recommendation=suggestion.explanation or "Monitor system closely",
                urgency=urgency
            )
            
        except Exception as e:
            print(f"Error creating prediction: {e}")
            return None
    
    async def _check_immediate_issues(self) -> List[Prediction]:
        """Check for immediate system issues."""
        predictions = []
        
        try:
            if not self.history:
                return predictions
            
            current = self.history[-1]
            
            # Check CPU
            if 'cpu' in current and current['cpu']['percent'] > self.cpu_threshold:
                predictions.append(Prediction(
                    type="cpu_high",
                    description=f"CPU usage is {current['cpu']['percent']}%",
                    confidence=0.95,
                    timeframe="immediate",
                    impact="high",
                    recommendation="Close unnecessary applications or optimize running processes",
                    urgency="high"
                ))
            
            # Check memory
            if 'memory' in current and current['memory']['percent'] > self.memory_threshold:
                predictions.append(Prediction(
                    type="memory_high",
                    description=f"Memory usage is {current['memory']['percent']}%",
                    confidence=0.95,
                    timeframe="immediate",
                    impact="high",
                    recommendation="Free up memory or add more RAM",
                    urgency="high"
                ))
            
            # Check disk
            if 'disk' in current and current['disk']['percent'] > self.disk_threshold:
                predictions.append(Prediction(
                    type="disk_high",
                    description=f"Disk usage is {current['disk']['percent']}%",
                    confidence=0.95,
                    timeframe="immediate",
                    impact="high",
                    recommendation="Free up disk space immediately",
                    urgency="high"
                ))
            
            # Check temperature
            if 'temperature' in current and current['temperature']['cpu'] and current['temperature']['cpu'] > self.temperature_threshold:
                predictions.append(Prediction(
                    type="temperature_high",
                    description=f"CPU temperature is {current['temperature']['cpu']}°C",
                    confidence=0.9,
                    timeframe="immediate",
                    impact="high",
                    recommendation="Check cooling system and reduce CPU load",
                    urgency="high"
                ))
            
        except Exception as e:
            print(f"Error checking immediate issues: {e}")
        
        return predictions
    
    async def get_predictions(self, filter_type: str = None) -> List[Dict[str, Any]]:
        """Get current predictions."""
        predictions = []
        
        for pred in self.predictions:
            if filter_type and pred.type != filter_type:
                continue
            
            predictions.append({
                "type": pred.type,
                "description": pred.description,
                "confidence": pred.confidence,
                "timeframe": pred.timeframe,
                "impact": pred.impact,
                "recommendation": pred.recommendation,
                "urgency": pred.urgency
            })
        
        return predictions
    
    async def get_system_health_forecast(self) -> Dict[str, Any]:
        """Get system health forecast."""
        try:
            if not self.history:
                return {"error": "No historical data available"}
            
            # Analyze current trends
            trends = await self._analyze_trends()
            
            # Generate forecast
            forecast = {
                "current_status": "healthy",
                "forecast_1h": "stable",
                "forecast_6h": "stable",
                "forecast_24h": "stable",
                "risks": [],
                "recommendations": []
            }
            
            # Check for risks
            for trend in trends:
                if trend.change_rate > 1 and trend.current_value > 70:
                    forecast["risks"].append({
                        "metric": trend.metric,
                        "risk_level": "high" if trend.current_value > 85 else "medium",
                        "description": f"{trend.metric} is {trend.trend} and may cause issues"
                    })
            
            # Generate recommendations
            if forecast["risks"]:
                forecast["current_status"] = "warning"
                forecast["recommendations"].append("Monitor system closely and consider preventive measures")
            
            # Use AI for more detailed analysis
            context = f"""
            System Trends: {[f"{t.metric}: {t.current_value}% ({t.trend})" for t in trends]}
            Current Risks: {len(forecast['risks'])}
            """
            
            query = UserQuery(query=f"Provide a system health forecast: {context}")
            system_context = SystemContext(
                processes=[],
                memory_usage=0,
                cpu_usage=0,
                disk_usage=0
            )
            
            suggestion = await self.llm_manager.generate_suggestion(query, system_context)
            
            if suggestion.explanation:
                forecast["ai_analysis"] = suggestion.explanation
            
            return forecast
            
        except Exception as e:
            return {"error": f"Failed to generate forecast: {str(e)}"}
    
    async def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Get AI-powered optimization recommendations."""
        try:
            if not self.history:
                return []
            
            current = self.history[-1]
            recommendations = []
            
            # CPU optimization
            if 'cpu' in current and current['cpu']['percent'] > 50:
                recommendations.append({
                    "type": "cpu_optimization",
                    "priority": "high" if current['cpu']['percent'] > 80 else "medium",
                    "description": "High CPU usage detected",
                    "action": "Close unnecessary applications or optimize running processes",
                    "ai_insight": "Consider using process optimization tools"
                })
            
            # Memory optimization
            if 'memory' in current and current['memory']['percent'] > 70:
                recommendations.append({
                    "type": "memory_optimization",
                    "priority": "high" if current['memory']['percent'] > 90 else "medium",
                    "description": "High memory usage detected",
                    "action": "Free up memory or add more RAM",
                    "ai_insight": "Consider implementing memory management strategies"
                })
            
            # Disk optimization
            if 'disk' in current and current['disk']['percent'] > 80:
                recommendations.append({
                    "type": "disk_optimization",
                    "priority": "high" if current['disk']['percent'] > 95 else "medium",
                    "description": "Low disk space detected",
                    "action": "Clean up unnecessary files or add more storage",
                    "ai_insight": "Consider implementing automated cleanup routines"
                })
            
            return recommendations
            
        except Exception as e:
            return [{"error": f"Failed to get recommendations: {str(e)}"}]


async def main():
    """Main entry point for Predictive AI."""
    predictive_ai = PredictiveAI()
    
    print("🐋 Orca Predictive AI Assistant")
    print("=" * 50)
    
    # Start monitoring
    print("Starting predictive monitoring...")
    monitoring_task = asyncio.create_task(predictive_ai.start_monitoring(interval=30))
    
    try:
        # Let it run for a bit
        await asyncio.sleep(60)
        
        # Get predictions
        predictions = await predictive_ai.get_predictions()
        print(f"\nCurrent Predictions: {len(predictions)}")
        for pred in predictions:
            print(f"  • {pred['description']} (Confidence: {pred['confidence']:.1%})")
        
        # Get forecast
        forecast = await predictive_ai.get_system_health_forecast()
        if "error" not in forecast:
            print(f"\nSystem Health Forecast:")
            print(f"  Status: {forecast['current_status']}")
            print(f"  Risks: {len(forecast['risks'])}")
            print(f"  Recommendations: {len(forecast['recommendations'])}")
        
        # Get optimization recommendations
        recommendations = await predictive_ai.get_optimization_recommendations()
        print(f"\nOptimization Recommendations: {len(recommendations)}")
        for rec in recommendations:
            print(f"  • {rec['description']} ({rec['priority']} priority)")
        
    finally:
        # Stop monitoring
        predictive_ai.stop_monitoring()
        monitoring_task.cancel()


if __name__ == "__main__":
    asyncio.run(main())
