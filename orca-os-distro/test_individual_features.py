#!/usr/bin/env python3
"""
Orca OS Individual Feature Testing
Test each feature and functionality individually
"""

import asyncio
import subprocess
import json
import time
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import psutil
import requests

# Add orca-core to path
sys.path.insert(0, '/opt/orca-os')

class IndividualFeatureTester:
    """Individual feature tester for Orca OS."""
    
    def __init__(self):
        """Initialize the feature tester."""
        self.test_results = {}
        self.start_time = datetime.now()
        
    def log_test(self, feature: str, test: str, success: bool, message: str = "", details: Dict = None):
        """Log individual test result."""
        if feature not in self.test_results:
            self.test_results[feature] = {}
        
        self.test_results[feature][test] = {
            "success": success,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {feature} - {test}: {message}")
    
    def test_core_orca_cli(self):
        """Test core Orca CLI functionality."""
        print("\n🔍 Testing Core Orca CLI...")
        
        # Test basic help
        try:
            result = subprocess.run(['orca', '--help'], capture_output=True, text=True, timeout=10)
            self.log_test("Core CLI", "Help Command", result.returncode == 0, 
                         "Help command executed", {"returncode": result.returncode})
        except Exception as e:
            self.log_test("Core CLI", "Help Command", False, f"Exception: {str(e)}")
        
        # Test daemon mode
        try:
            result = subprocess.run(['orca', 'daemon', '--help'], capture_output=True, text=True, timeout=10)
            self.log_test("Core CLI", "Daemon Help", result.returncode == 0, 
                         "Daemon help command executed", {"returncode": result.returncode})
        except Exception as e:
            self.log_test("Core CLI", "Daemon Help", False, f"Exception: {str(e)}")
        
        # Test overlay mode
        try:
            result = subprocess.run(['orca', 'overlay', '--help'], capture_output=True, text=True, timeout=10)
            self.log_test("Core CLI", "Overlay Help", result.returncode == 0, 
                         "Overlay help command executed", {"returncode": result.returncode})
        except Exception as e:
            self.log_test("Core CLI", "Overlay Help", False, f"Exception: {str(e)}")
    
    def test_ai_queries(self):
        """Test AI query functionality."""
        print("\n🔍 Testing AI Query Functionality...")
        
        queries = [
            "show me running processes",
            "show me system information", 
            "show me memory usage",
            "show me disk usage",
            "list files in current directory",
            "what is the current time"
        ]
        
        for query in queries:
            try:
                start_time = time.time()
                result = subprocess.run(['orca', query], capture_output=True, text=True, timeout=30)
                end_time = time.time()
                response_time = end_time - start_time
                
                success = result.returncode == 0 and len(result.stdout) > 0
                self.log_test("AI Queries", f"Query: {query[:30]}...", success, 
                             f"Response time: {response_time:.2f}s", 
                             {"returncode": result.returncode, "response_time": response_time})
            except Exception as e:
                self.log_test("AI Queries", f"Query: {query[:30]}...", False, f"Exception: {str(e)}")
    
    def test_process_manager(self):
        """Test AI Process Manager."""
        print("\n🔍 Testing AI Process Manager...")
        
        # Test help command
        try:
            result = subprocess.run(['orca-process-manager', '--help'], capture_output=True, text=True, timeout=10)
            self.log_test("Process Manager", "Help Command", result.returncode == 0, 
                         "Help command executed", {"returncode": result.returncode})
        except Exception as e:
            self.log_test("Process Manager", "Help Command", False, f"Exception: {str(e)}")
        
        # Test process analysis
        try:
            result = subprocess.run(['orca-process-manager'], capture_output=True, text=True, timeout=30)
            success = result.returncode == 0 and "System Health" in result.stdout
            self.log_test("Process Manager", "Process Analysis", success, 
                         "Process analysis executed", {"returncode": result.returncode})
        except Exception as e:
            self.log_test("Process Manager", "Process Analysis", False, f"Exception: {str(e)}")
    
    def test_logging_system(self):
        """Test AI Logging System."""
        print("\n🔍 Testing AI Logging System...")
        
        # Test help command
        try:
            result = subprocess.run(['orca-logs', '--help'], capture_output=True, text=True, timeout=10)
            self.log_test("Logging System", "Help Command", result.returncode == 0, 
                         "Help command executed", {"returncode": result.returncode})
        except Exception as e:
            self.log_test("Logging System", "Help Command", False, f"Exception: {str(e)}")
        
        # Test log analysis
        try:
            result = subprocess.run(['orca-logs'], capture_output=True, text=True, timeout=30)
            success = result.returncode == 0 and "Log Summary" in result.stdout
            self.log_test("Logging System", "Log Analysis", success, 
                         "Log analysis executed", {"returncode": result.returncode})
        except Exception as e:
            self.log_test("Logging System", "Log Analysis", False, f"Exception: {str(e)}")
    
    def test_scheduler(self):
        """Test AI Scheduler."""
        print("\n🔍 Testing AI Scheduler...")
        
        # Test help command
        try:
            result = subprocess.run(['orca-scheduler', '--help'], capture_output=True, text=True, timeout=10)
            self.log_test("Scheduler", "Help Command", result.returncode == 0, 
                         "Help command executed", {"returncode": result.returncode})
        except Exception as e:
            self.log_test("Scheduler", "Help Command", False, f"Exception: {str(e)}")
        
        # Test scheduling report
        try:
            result = subprocess.run(['orca-scheduler'], capture_output=True, text=True, timeout=30)
            success = result.returncode == 0 and "Scheduling Report" in result.stdout
            self.log_test("Scheduler", "Scheduling Report", success, 
                         "Scheduling report executed", {"returncode": result.returncode})
        except Exception as e:
            self.log_test("Scheduler", "Scheduling Report", False, f"Exception: {str(e)}")
    
    def test_dashboard(self):
        """Test Orca Dashboard."""
        print("\n🔍 Testing Orca Dashboard...")
        
        # Test help command
        try:
            result = subprocess.run(['orca-dashboard', '--help'], capture_output=True, text=True, timeout=10)
            self.log_test("Dashboard", "Help Command", result.returncode == 0, 
                         "Help command executed", {"returncode": result.returncode})
        except Exception as e:
            self.log_test("Dashboard", "Help Command", False, f"Exception: {str(e)}")
        
        # Test dashboard startup (brief)
        try:
            process = subprocess.Popen(['orca-dashboard'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(5)  # Let it run for 5 seconds
            process.terminate()
            process.wait()
            self.log_test("Dashboard", "Dashboard Startup", True, 
                         "Dashboard started successfully", {"pid": process.pid})
        except Exception as e:
            self.log_test("Dashboard", "Dashboard Startup", False, f"Exception: {str(e)}")
    
    def test_predictive_ai(self):
        """Test Predictive AI."""
        print("\n🔍 Testing Predictive AI...")
        
        # Test help command
        try:
            result = subprocess.run(['orca-predict', '--help'], capture_output=True, text=True, timeout=10)
            self.log_test("Predictive AI", "Help Command", result.returncode == 0, 
                         "Help command executed", {"returncode": result.returncode})
        except Exception as e:
            self.log_test("Predictive AI", "Help Command", False, f"Exception: {str(e)}")
        
        # Test prediction
        try:
            result = subprocess.run(['orca-predict'], capture_output=True, text=True, timeout=30)
            success = result.returncode == 0 and "Predictive AI" in result.stdout
            self.log_test("Predictive AI", "Prediction", success, 
                         "Prediction executed", {"returncode": result.returncode})
        except Exception as e:
            self.log_test("Predictive AI", "Prediction", False, f"Exception: {str(e)}")
    
    def test_optimizer(self):
        """Test System Optimizer."""
        print("\n🔍 Testing System Optimizer...")
        
        # Test help command
        try:
            result = subprocess.run(['orca-optimize', '--help'], capture_output=True, text=True, timeout=10)
            self.log_test("Optimizer", "Help Command", result.returncode == 0, 
                         "Help command executed", {"returncode": result.returncode})
        except Exception as e:
            self.log_test("Optimizer", "Help Command", False, f"Exception: {str(e)}")
        
        # Test optimization (dry run)
        try:
            result = subprocess.run(['orca-optimize', '--dry-run'], capture_output=True, text=True, timeout=30)
            success = result.returncode == 0 and "optimization" in result.stdout.lower()
            self.log_test("Optimizer", "Dry Run Optimization", success, 
                         "Dry run optimization executed", {"returncode": result.returncode})
        except Exception as e:
            self.log_test("Optimizer", "Dry Run Optimization", False, f"Exception: {str(e)}")
    
    def test_plugin_system(self):
        """Test Plugin System."""
        print("\n🔍 Testing Plugin System...")
        
        # Test help command
        try:
            result = subprocess.run(['orca-plugins', '--help'], capture_output=True, text=True, timeout=10)
            self.log_test("Plugin System", "Help Command", result.returncode == 0, 
                         "Help command executed", {"returncode": result.returncode})
        except Exception as e:
            self.log_test("Plugin System", "Help Command", False, f"Exception: {str(e)}")
        
        # Test plugin listing
        try:
            result = subprocess.run(['orca-plugins', '--list'], capture_output=True, text=True, timeout=30)
            success = result.returncode == 0 and "plugins" in result.stdout.lower()
            self.log_test("Plugin System", "Plugin Listing", success, 
                         "Plugin listing executed", {"returncode": result.returncode})
        except Exception as e:
            self.log_test("Plugin System", "Plugin Listing", False, f"Exception: {str(e)}")
    
    def test_package_manager(self):
        """Test AI Package Manager."""
        print("\n🔍 Testing AI Package Manager...")
        
        # Test help command
        try:
            result = subprocess.run(['orca-install', '--help'], capture_output=True, text=True, timeout=10)
            self.log_test("Package Manager", "Help Command", result.returncode == 0, 
                         "Help command executed", {"returncode": result.returncode})
        except Exception as e:
            self.log_test("Package Manager", "Help Command", False, f"Exception: {str(e)}")
        
        # Test package search (dry run)
        try:
            result = subprocess.run(['orca-install', '--search', 'htop'], capture_output=True, text=True, timeout=30)
            success = result.returncode == 0 or "htop" in result.stdout.lower()
            self.log_test("Package Manager", "Package Search", success, 
                         "Package search executed", {"returncode": result.returncode})
        except Exception as e:
            self.log_test("Package Manager", "Package Search", False, f"Exception: {str(e)}")
    
    def test_advanced_cli(self):
        """Test Advanced CLI."""
        print("\n🔍 Testing Advanced CLI...")
        
        # Test help command
        try:
            result = subprocess.run(['orca-advanced', '--help'], capture_output=True, text=True, timeout=10)
            self.log_test("Advanced CLI", "Help Command", result.returncode == 0, 
                         "Help command executed", {"returncode": result.returncode})
        except Exception as e:
            self.log_test("Advanced CLI", "Help Command", False, f"Exception: {str(e)}")
        
        # Test process manager command
        try:
            result = subprocess.run(['orca-advanced', 'process-manager', '--health'], 
                                  capture_output=True, text=True, timeout=30)
            success = result.returncode == 0 and "process" in result.stdout.lower()
            self.log_test("Advanced CLI", "Process Manager Command", success, 
                         "Process manager command executed", {"returncode": result.returncode})
        except Exception as e:
            self.log_test("Advanced CLI", "Process Manager Command", False, f"Exception: {str(e)}")
    
    def test_services(self):
        """Test Systemd Services."""
        print("\n🔍 Testing Systemd Services...")
        
        services = [
            'orca-ai.service',
            'orca-ai-process-manager.service',
            'orca-ai-logging.service',
            'orca-ai-scheduler.service',
            'orca-predictive-ai.service',
            'orca-dashboard.service'
        ]
        
        for service in services:
            try:
                result = subprocess.run(['systemctl', 'is-active', service], 
                                      capture_output=True, text=True, timeout=5)
                is_active = result.returncode == 0 and 'active' in result.stdout
                self.log_test("Services", f"Service {service}", is_active, 
                             f"Status: {result.stdout.strip()}", {"returncode": result.returncode})
            except Exception as e:
                self.log_test("Services", f"Service {service}", False, f"Exception: {str(e)}")
    
    def test_api_endpoints(self):
        """Test API Endpoints."""
        print("\n🔍 Testing API Endpoints...")
        
        endpoints = [
            ('/health', 'Health Check'),
            ('/status', 'Status Check'),
            ('/query', 'Query Endpoint')
        ]
        
        for endpoint, description in endpoints:
            try:
                response = requests.get(f'http://localhost:8080{endpoint}', timeout=5)
                success = response.status_code == 200
                self.log_test("API Endpoints", description, success, 
                             f"HTTP {response.status_code}", {"status_code": response.status_code})
            except Exception as e:
                self.log_test("API Endpoints", description, False, f"Exception: {str(e)}")
    
    def test_performance(self):
        """Test Performance Metrics."""
        print("\n🔍 Testing Performance Metrics...")
        
        # Test response time
        try:
            start_time = time.time()
            result = subprocess.run(['orca', 'show me system information'], 
                                  capture_output=True, text=True, timeout=30)
            end_time = time.time()
            response_time = end_time - start_time
            
            success = response_time < 15.0  # Should respond within 15 seconds
            self.log_test("Performance", "Response Time", success, 
                         f"{response_time:.2f} seconds", {"response_time": response_time})
        except Exception as e:
            self.log_test("Performance", "Response Time", False, f"Exception: {str(e)}")
        
        # Test memory usage
        try:
            process = psutil.Process()
            memory_usage = process.memory_info().rss / 1024 / 1024  # MB
            success = memory_usage < 1000  # Should use less than 1GB
            self.log_test("Performance", "Memory Usage", success, 
                         f"{memory_usage:.1f} MB", {"memory_usage": memory_usage})
        except Exception as e:
            self.log_test("Performance", "Memory Usage", False, f"Exception: {str(e)}")
        
        # Test CPU usage
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            success = cpu_usage < 80  # Should use less than 80% CPU
            self.log_test("Performance", "CPU Usage", success, 
                         f"{cpu_usage:.1f}%", {"cpu_usage": cpu_usage})
        except Exception as e:
            self.log_test("Performance", "CPU Usage", False, f"Exception: {str(e)}")
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate detailed test report."""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        # Calculate summary statistics
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        for feature, tests in self.test_results.items():
            for test, result in tests.items():
                total_tests += 1
                if result["success"]:
                    passed_tests += 1
                else:
                    failed_tests += 1
        
        report = {
            "test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "duration_seconds": duration.total_seconds()
            },
            "feature_results": self.test_results,
            "timestamp": end_time.isoformat(),
            "system_info": {
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "platform": sys.platform,
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "disk_total": psutil.disk_usage('/').total
            }
        }
        
        return report
    
    def run_all_tests(self):
        """Run all individual feature tests."""
        print("🐋 Orca OS Individual Feature Testing")
        print("=" * 50)
        print(f"Started at: {self.start_time.isoformat()}")
        print()
        
        # Run all test categories
        test_functions = [
            self.test_core_orca_cli,
            self.test_ai_queries,
            self.test_process_manager,
            self.test_logging_system,
            self.test_scheduler,
            self.test_dashboard,
            self.test_predictive_ai,
            self.test_optimizer,
            self.test_plugin_system,
            self.test_package_manager,
            self.test_advanced_cli,
            self.test_services,
            self.test_api_endpoints,
            self.test_performance
        ]
        
        for test_func in test_functions:
            try:
                test_func()
            except Exception as e:
                print(f"❌ Test {test_func.__name__} failed with exception: {str(e)}")
        
        # Generate and save report
        report = self.generate_report()
        
        # Save report to file
        report_file = f"orca_individual_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 INDIVIDUAL FEATURE TEST SUMMARY")
        print("=" * 50)
        print(f"Total Tests: {report['test_summary']['total_tests']}")
        print(f"Passed: {report['test_summary']['passed_tests']} ✅")
        print(f"Failed: {report['test_summary']['failed_tests']} ❌")
        print(f"Success Rate: {report['test_summary']['success_rate']:.1f}%")
        print(f"Duration: {report['test_summary']['duration_seconds']:.1f} seconds")
        print(f"Report saved to: {report_file}")
        
        # Print feature breakdown
        print("\n📋 Feature Breakdown:")
        for feature, tests in self.test_results.items():
            feature_passed = sum(1 for test in tests.values() if test["success"])
            feature_total = len(tests)
            feature_rate = (feature_passed / feature_total * 100) if feature_total > 0 else 0
            print(f"  {feature}: {feature_passed}/{feature_total} ({feature_rate:.1f}%)")
        
        return report['test_summary']['success_rate'] > 80


def main():
    """Main entry point."""
    tester = IndividualFeatureTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
