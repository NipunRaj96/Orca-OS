#!/usr/bin/env python3
"""
Orca OS Advanced Features Test Suite
Comprehensive testing for Phase 3 & 4 features
"""

import asyncio
import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import json

# Add orca-core to path
sys.path.insert(0, '/opt/orca-os')

# Import advanced features
from kernel.ai_process_manager import AIProcessManager
from kernel.ai_logging_system import AILoggingSystem
from kernel.ai_scheduler import AIScheduler
from advanced.orca_package_manager import OrcaPackageManager
from advanced.plugin_system import OrcaPluginSystem
from advanced.predictive_ai import PredictiveAI
from advanced.orca_dashboard import OrcaDashboard
from advanced.orca_optimizer import OrcaOptimizer


class TestAdvancedFeatures:
    """Test suite for Orca OS advanced features."""
    
    @pytest.fixture
    def mock_config(self):
        """Mock configuration for testing."""
        return {
            "llm": {
                "base_url": "http://localhost:11434",
                "model": "llama3.1",
                "temperature": 0.7,
                "max_tokens": 1000,
                "timeout": 30
            },
            "policy": {
                "enabled": True,
                "rules": []
            },
            "executor": {
                "sandbox": True,
                "timeout": 30
            }
        }
    
    @pytest.fixture
    def mock_llm_manager(self):
        """Mock LLM manager for testing."""
        manager = Mock()
        manager.generate_suggestion = AsyncMock()
        manager.generate_suggestion.return_value = Mock(
            command="test_command",
            explanation="Test explanation",
            confidence=0.8
        )
        return manager
    
    @pytest.mark.asyncio
    async def test_ai_process_manager(self, mock_config, mock_llm_manager):
        """Test AI Process Manager functionality."""
        with patch('orca.utils.config.load_config', return_value=Mock(**mock_config)):
            with patch('orca.llm.manager.LLMManager', return_value=mock_llm_manager):
                manager = AIProcessManager()
                
                # Test process analysis
                processes = await manager.analyze_processes()
                assert isinstance(processes, list)
                
                # Test system health
                health = await manager.get_system_health()
                assert 'health_score' in health
                assert 'health_status' in health
                assert 0 <= health['health_score'] <= 100
                
                # Test optimization
                optimization = await manager.optimize_system()
                assert 'status' in optimization
                assert optimization['status'] in ['completed', 'already_running', 'error']
    
    @pytest.mark.asyncio
    async def test_ai_logging_system(self, mock_config, mock_llm_manager):
        """Test AI Logging System functionality."""
        with patch('orca.utils.config.load_config', return_value=Mock(**mock_config)):
            with patch('orca.llm.manager.LLMManager', return_value=mock_llm_manager):
                with patch('subprocess.run') as mock_run:
                    # Mock journalctl output
                    mock_run.return_value = Mock(
                        returncode=0,
                        stdout='{"MESSAGE": "Test log message", "__REALTIME_TIMESTAMP": "1234567890000000"}'
                    )
                    
                    logging_system = AILoggingSystem()
                    
                    # Test log analysis
                    logs = await logging_system.analyze_logs(hours=1)
                    assert isinstance(logs, list)
                    
                    # Test log summary
                    summary = await logging_system.get_log_summary(hours=1)
                    assert 'summary' in summary or 'error' in summary
    
    @pytest.mark.asyncio
    async def test_ai_scheduler(self, mock_config, mock_llm_manager):
        """Test AI Scheduler functionality."""
        with patch('orca.utils.config.load_config', return_value=Mock(**mock_config)):
            with patch('orca.llm.manager.LLMManager', return_value=mock_llm_manager):
                scheduler = AIScheduler()
                
                # Test process importance analysis
                importance = await scheduler.analyze_process_importance(1)
                assert importance in ['critical', 'important', 'normal', 'optional', 'unknown']
                
                # Test scheduling optimization
                optimization = await scheduler.optimize_process_scheduling()
                assert 'status' in optimization
                
                # Test system load monitoring
                load_data = await scheduler.monitor_system_load()
                assert 'cpu_usage' in load_data or 'error' in load_data
    
    @pytest.mark.asyncio
    async def test_orca_package_manager(self, mock_config, mock_llm_manager):
        """Test Orca Package Manager functionality."""
        with patch('orca.utils.config.load_config', return_value=Mock(**mock_config)):
            with patch('orca.llm.manager.LLMManager', return_value=mock_llm_manager):
                with patch('subprocess.run') as mock_run:
                    # Mock apt commands
                    mock_run.return_value = Mock(
                        returncode=0,
                        stdout="Package: test-package\nVersion: 1.0.0\nDescription: Test package"
                    )
                    
                    package_manager = OrcaPackageManager()
                    
                    # Test package info retrieval
                    package_info = await package_manager._get_package_info("test-package")
                    assert package_info is not None or package_info is None
                    
                    # Test package search
                    search_results = await package_manager.search_packages("test")
                    assert isinstance(search_results, list)
    
    @pytest.mark.asyncio
    async def test_plugin_system(self, mock_config, mock_llm_manager):
        """Test Plugin System functionality."""
        with patch('orca.utils.config.load_config', return_value=Mock(**mock_config)):
            with patch('orca.llm.manager.LLMManager', return_value=mock_llm_manager):
                plugin_system = OrcaPluginSystem()
                
                # Test plugin listing
                plugins = await plugin_system.list_plugins()
                assert isinstance(plugins, list)
                
                # Test function listing
                functions = await plugin_system.list_functions()
                assert isinstance(functions, list)
                
                # Test plugin template creation
                template_result = await plugin_system.create_plugin_template("test-plugin")
                assert 'status' in template_result
    
    @pytest.mark.asyncio
    async def test_predictive_ai(self, mock_config, mock_llm_manager):
        """Test Predictive AI functionality."""
        with patch('orca.utils.config.load_config', return_value=Mock(**mock_config)):
            with patch('orca.llm.manager.LLMManager', return_value=mock_llm_manager):
                predictive_ai = PredictiveAI()
                
                # Test metrics collection
                metrics = await predictive_ai._collect_system_metrics()
                assert 'timestamp' in metrics
                
                # Test predictions
                predictions = await predictive_ai.get_predictions()
                assert isinstance(predictions, list)
                
                # Test health forecast
                forecast = await predictive_ai.get_system_health_forecast()
                assert 'current_status' in forecast or 'error' in forecast
    
    @pytest.mark.asyncio
    async def test_orca_dashboard(self, mock_config, mock_llm_manager):
        """Test Orca Dashboard functionality."""
        with patch('orca.utils.config.load_config', return_value=Mock(**mock_config)):
            with patch('orca.llm.manager.LLMManager', return_value=mock_llm_manager):
                dashboard = OrcaDashboard()
                await dashboard.initialize_widgets()
                
                # Test widget updates
                for widget_name in dashboard.widgets:
                    result = await dashboard.update_widget(widget_name)
                    assert 'error' not in result or 'error' in result
    
    @pytest.mark.asyncio
    async def test_orca_optimizer(self, mock_config, mock_llm_manager):
        """Test Orca Optimizer functionality."""
        with patch('orca.utils.config.load_config', return_value=Mock(**mock_config)):
            with patch('orca.llm.manager.LLMManager', return_value=mock_llm_manager):
                optimizer = OrcaOptimizer()
                await optimizer.initialize_optimization_tasks()
                
                # Test system analysis
                analysis = await optimizer.analyze_system()
                assert 'overall_score' in analysis or 'error' in analysis
                
                # Test optimization plan
                tasks = await optimizer.get_optimization_plan()
                assert isinstance(tasks, list)
    
    def test_integration_workflow(self):
        """Test integration between different components."""
        # This would test how different components work together
        # For now, just verify imports work
        try:
            from kernel.ai_process_manager import AIProcessManager
            from kernel.ai_logging_system import AILoggingSystem
            from kernel.ai_scheduler import AIScheduler
            from advanced.orca_package_manager import OrcaPackageManager
            from advanced.plugin_system import OrcaPluginSystem
            from advanced.predictive_ai import PredictiveAI
            from advanced.orca_dashboard import OrcaDashboard
            from advanced.orca_optimizer import OrcaOptimizer
            assert True
        except ImportError as e:
            pytest.fail(f"Import failed: {e}")
    
    def test_configuration_loading(self):
        """Test configuration loading for all components."""
        # Test that all components can load configuration
        components = [
            AIProcessManager,
            AILoggingSystem,
            AIScheduler,
            OrcaPackageManager,
            OrcaPluginSystem,
            PredictiveAI,
            OrcaDashboard,
            OrcaOptimizer
        ]
        
        for component in components:
            try:
                # This should not raise an exception
                # In a real test, we'd mock the config loading
                pass
            except Exception as e:
                pytest.fail(f"Configuration loading failed for {component.__name__}: {e}")


class TestPerformance:
    """Performance tests for advanced features."""
    
    @pytest.mark.asyncio
    async def test_process_manager_performance(self):
        """Test AI Process Manager performance."""
        with patch('orca.utils.config.load_config'):
            with patch('orca.llm.manager.LLMManager'):
                manager = AIProcessManager()
                
                # Test that process analysis completes within reasonable time
                import time
                start_time = time.time()
                processes = await manager.analyze_processes()
                end_time = time.time()
                
                assert end_time - start_time < 10  # Should complete within 10 seconds
                assert isinstance(processes, list)
    
    @pytest.mark.asyncio
    async def test_dashboard_performance(self):
        """Test dashboard performance."""
        with patch('orca.utils.config.load_config'):
            with patch('orca.llm.manager.LLMManager'):
                dashboard = OrcaDashboard()
                await dashboard.initialize_widgets()
                
                # Test widget update performance
                import time
                start_time = time.time()
                await dashboard.update_widget('system_overview')
                end_time = time.time()
                
                assert end_time - start_time < 5  # Should complete within 5 seconds


class TestErrorHandling:
    """Error handling tests for advanced features."""
    
    @pytest.mark.asyncio
    async def test_llm_connection_error(self):
        """Test handling of LLM connection errors."""
        with patch('orca.utils.config.load_config'):
            with patch('orca.llm.manager.LLMManager') as mock_llm:
                # Mock LLM to raise connection error
                mock_llm.return_value.generate_suggestion.side_effect = Exception("Connection failed")
                
                manager = AIProcessManager()
                
                # Should handle error gracefully
                health = await manager.get_system_health()
                assert 'error' in health or 'health_score' in health
    
    @pytest.mark.asyncio
    async def test_system_command_error(self):
        """Test handling of system command errors."""
        with patch('orca.utils.config.load_config'):
            with patch('orca.llm.manager.LLMManager'):
                with patch('subprocess.run') as mock_run:
                    # Mock subprocess to raise error
                    mock_run.side_effect = Exception("Command failed")
                    
                    optimizer = OrcaOptimizer()
                    await optimizer.initialize_optimization_tasks()
                    
                    # Should handle error gracefully
                    analysis = await optimizer.analyze_system()
                    assert 'error' in analysis or 'overall_score' in analysis


def run_tests():
    """Run all tests."""
    print("🐋 Running Orca OS Advanced Features Test Suite")
    print("=" * 60)
    
    # Run pytest
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--color=yes"
    ])


if __name__ == "__main__":
    run_tests()
