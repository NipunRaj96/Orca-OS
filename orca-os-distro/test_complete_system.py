#!/usr/bin/env python3
"""
Orca OS Complete System Test Suite
Comprehensive testing of all features and functionality
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

class OrcaSystemTester:
    """Comprehensive system tester for Orca OS."""
    
    def __init__(self):
        """Initialize the system tester."""
        self.test_results = {}
        self.start_time = datetime.now()
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test result."""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            self.failed_tests += 1
            status = "❌ FAIL"
        
        self.test_results[test_name] = {
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"{status} {test_name}: {message}")
    
    def test_system_requirements(self) -> bool:
        """Test system requirements."""
        print("\n🔍 Testing System Requirements...")
        
        # Test Python version
        python_version = sys.version_info
        if python_version.major >= 3 and python_version.minor >= 8:
            self.log_test("Python Version", True, f"Python {python_version.major}.{python_version.minor}")
        else:
            self.log_test("Python Version", False, f"Python {python_version.major}.{python_version.minor} (requires 3.8+)")
            return False
        
        # Test required packages
        required_packages = ['psutil', 'requests', 'asyncio']
        for package in required_packages:
            try:
                __import__(package)
                self.log_test(f"Package {package}", True, "Available")
            except ImportError:
                self.log_test(f"Package {package}", False, "Not available")
                return False
        
        # Test Orca OS installation
        orca_path = Path("/opt/orca-os")
        if orca_path.exists():
            self.log_test("Orca OS Installation", True, "Found at /opt/orca-os")
        else:
            self.log_test("Orca OS Installation", False, "Not found at /opt/orca-os")
            return False
        
        return True
    
    def test_core_components(self) -> bool:
        """Test core Orca OS components."""
        print("\n🔍 Testing Core Components...")
        
        # Test Orca CLI
        try:
            result = subprocess.run(['orca', '--help'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.log_test("Orca CLI", True, "Available and responding")
            else:
                self.log_test("Orca CLI", False, f"Error: {result.stderr}")
                return False
        except Exception as e:
            self.log_test("Orca CLI", False, f"Exception: {str(e)}")
            return False
        
        # Test Orca Daemon
        try:
            result = subprocess.run(['systemctl', 'is-active', 'orca-ai.service'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and 'active' in result.stdout:
                self.log_test("Orca Daemon", True, "Running")
            else:
                self.log_test("Orca Daemon", False, "Not running")
                return False
        except Exception as e:
            self.log_test("Orca Daemon", False, f"Exception: {str(e)}")
            return False
        
        # Test Ollama connection
        try:
            response = requests.get('http://localhost:11434/api/tags', timeout=5)
            if response.status_code == 200:
                self.log_test("Ollama Connection", True, "Connected")
            else:
                self.log_test("Ollama Connection", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Ollama Connection", False, f"Exception: {str(e)}")
            return False
        
        return True
    
    def test_phase3_features(self) -> bool:
        """Test Phase 3: Kernel & System Integration features."""
        print("\n🔍 Testing Phase 3: Kernel & System Integration...")
        
        # Test AI Process Manager
        try:
            result = subprocess.run(['orca-process-manager', '--help'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.log_test("AI Process Manager", True, "Available")
            else:
                self.log_test("AI Process Manager", False, f"Error: {result.stderr}")
        except Exception as e:
            self.log_test("AI Process Manager", False, f"Exception: {str(e)}")
        
        # Test AI Logging System
        try:
            result = subprocess.run(['orca-logs', '--help'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.log_test("AI Logging System", True, "Available")
            else:
                self.log_test("AI Logging System", False, f"Error: {result.stderr}")
        except Exception as e:
            self.log_test("AI Logging System", False, f"Exception: {str(e)}")
        
        # Test AI Scheduler
        try:
            result = subprocess.run(['orca-scheduler', '--help'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.log_test("AI Scheduler", True, "Available")
            else:
                self.log_test("AI Scheduler", False, f"Error: {result.stderr}")
        except Exception as e:
            self.log_test("AI Scheduler", False, f"Exception: {str(e)}")
        
        return True
    
    def test_phase4_features(self) -> bool:
        """Test Phase 4: Advanced Features."""
        print("\n🔍 Testing Phase 4: Advanced Features...")
        
        # Test Orca Dashboard
        try:
            result = subprocess.run(['orca-dashboard', '--help'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.log_test("Orca Dashboard", True, "Available")
            else:
                self.log_test("Orca Dashboard", False, f"Error: {result.stderr}")
        except Exception as e:
            self.log_test("Orca Dashboard", False, f"Exception: {str(e)}")
        
        # Test Predictive AI
        try:
            result = subprocess.run(['orca-predict', '--help'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.log_test("Predictive AI", True, "Available")
            else:
                self.log_test("Predictive AI", False, f"Error: {result.stderr}")
        except Exception as e:
            self.log_test("Predictive AI", False, f"Exception: {str(e)}")
        
        # Test System Optimizer
        try:
            result = subprocess.run(['orca-optimize', '--help'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.log_test("System Optimizer", True, "Available")
            else:
                self.log_test("System Optimizer", False, f"Error: {result.stderr}")
        except Exception as e:
            self.log_test("System Optimizer", False, f"Exception: {str(e)}")
        
        # Test Plugin System
        try:
            result = subprocess.run(['orca-plugins', '--help'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.log_test("Plugin System", True, "Available")
            else:
                self.log_test("Plugin System", False, f"Error: {result.stderr}")
        except Exception as e:
            self.log_test("Plugin System", False, f"Exception: {str(e)}")
        
        return True
    
    def test_ai_functionality(self) -> bool:
        """Test AI functionality."""
        print("\n🔍 Testing AI Functionality...")
        
        # Test basic AI query
        try:
            result = subprocess.run(['orca', 'show me running processes'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0 and 'process' in result.stdout.lower():
                self.log_test("Basic AI Query", True, "AI responded with process information")
            else:
                self.log_test("Basic AI Query", False, f"AI response: {result.stdout}")
        except Exception as e:
            self.log_test("Basic AI Query", False, f"Exception: {str(e)}")
        
        # Test system information query
        try:
            result = subprocess.run(['orca', 'show me system information'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                self.log_test("System Info Query", True, "AI provided system information")
            else:
                self.log_test("System Info Query", False, f"AI response: {result.stdout}")
        except Exception as e:
            self.log_test("System Info Query", False, f"Exception: {str(e)}")
        
        # Test memory usage query
        try:
            result = subprocess.run(['orca', 'show me memory usage'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                self.log_test("Memory Usage Query", True, "AI provided memory information")
            else:
                self.log_test("Memory Usage Query", False, f"AI response: {result.stdout}")
        except Exception as e:
            self.log_test("Memory Usage Query", False, f"Exception: {str(e)}")
        
        return True
    
    def test_performance(self) -> bool:
        """Test system performance."""
        print("\n🔍 Testing System Performance...")
        
        # Test response time
        start_time = time.time()
        try:
            result = subprocess.run(['orca', 'show me disk usage'], 
                                  capture_output=True, text=True, timeout=30)
            end_time = time.time()
            response_time = end_time - start_time
            
            if response_time < 10.0:  # Should respond within 10 seconds
                self.log_test("Response Time", True, f"{response_time:.2f} seconds")
            else:
                self.log_test("Response Time", False, f"{response_time:.2f} seconds (too slow)")
        except Exception as e:
            self.log_test("Response Time", False, f"Exception: {str(e)}")
        
        # Test memory usage
        try:
            process = psutil.Process()
            memory_usage = process.memory_info().rss / 1024 / 1024  # MB
            
            if memory_usage < 500:  # Should use less than 500MB
                self.log_test("Memory Usage", True, f"{memory_usage:.1f} MB")
            else:
                self.log_test("Memory Usage", False, f"{memory_usage:.1f} MB (too high)")
        except Exception as e:
            self.log_test("Memory Usage", False, f"Exception: {str(e)}")
        
        # Test CPU usage
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            if cpu_usage < 50:  # Should use less than 50% CPU
                self.log_test("CPU Usage", True, f"{cpu_usage:.1f}%")
            else:
                self.log_test("CPU Usage", False, f"{cpu_usage:.1f}% (too high)")
        except Exception as e:
            self.log_test("CPU Usage", False, f"Exception: {str(e)}")
        
        return True
    
    def test_services(self) -> bool:
        """Test systemd services."""
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
                if result.returncode == 0 and 'active' in result.stdout:
                    self.log_test(f"Service {service}", True, "Running")
                else:
                    self.log_test(f"Service {service}", False, "Not running")
            except Exception as e:
                self.log_test(f"Service {service}", False, f"Exception: {str(e)}")
        
        return True
    
    def test_integration(self) -> bool:
        """Test component integration."""
        print("\n🔍 Testing Component Integration...")
        
        # Test CLI integration
        try:
            result = subprocess.run(['orca-advanced', '--help'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.log_test("Advanced CLI Integration", True, "Available")
            else:
                self.log_test("Advanced CLI Integration", False, f"Error: {result.stderr}")
        except Exception as e:
            self.log_test("Advanced CLI Integration", False, f"Exception: {str(e)}")
        
        # Test API endpoints
        try:
            response = requests.get('http://localhost:8080/health', timeout=5)
            if response.status_code == 200:
                self.log_test("API Health Endpoint", True, "Responding")
            else:
                self.log_test("API Health Endpoint", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("API Health Endpoint", False, f"Exception: {str(e)}")
        
        return True
    
    def test_error_handling(self) -> bool:
        """Test error handling."""
        print("\n🔍 Testing Error Handling...")
        
        # Test invalid command
        try:
            result = subprocess.run(['orca', 'invalid_command_xyz'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                self.log_test("Invalid Command Handling", True, "Properly handled invalid command")
            else:
                self.log_test("Invalid Command Handling", False, "Should have failed")
        except Exception as e:
            self.log_test("Invalid Command Handling", False, f"Exception: {str(e)}")
        
        # Test empty query
        try:
            result = subprocess.run(['orca', ''], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                self.log_test("Empty Query Handling", True, "Properly handled empty query")
            else:
                self.log_test("Empty Query Handling", False, "Should have failed")
        except Exception as e:
            self.log_test("Empty Query Handling", False, f"Exception: {str(e)}")
        
        return True
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate test report."""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        report = {
            "test_summary": {
                "total_tests": self.total_tests,
                "passed_tests": self.passed_tests,
                "failed_tests": self.failed_tests,
                "success_rate": (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0,
                "duration_seconds": duration.total_seconds()
            },
            "test_results": self.test_results,
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
    
    def run_all_tests(self) -> bool:
        """Run all tests."""
        print("🐋 Orca OS Complete System Test Suite")
        print("=" * 50)
        print(f"Started at: {self.start_time.isoformat()}")
        print()
        
        # Run all test categories
        tests = [
            self.test_system_requirements,
            self.test_core_components,
            self.test_phase3_features,
            self.test_phase4_features,
            self.test_ai_functionality,
            self.test_performance,
            self.test_services,
            self.test_integration,
            self.test_error_handling
        ]
        
        for test_func in tests:
            try:
                test_func()
            except Exception as e:
                print(f"❌ Test {test_func.__name__} failed with exception: {str(e)}")
                self.failed_tests += 1
                self.total_tests += 1
        
        # Generate and save report
        report = self.generate_report()
        
        # Save report to file
        report_file = f"orca_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Success Rate: {report['test_summary']['success_rate']:.1f}%")
        print(f"Duration: {report['test_summary']['duration_seconds']:.1f} seconds")
        print(f"Report saved to: {report_file}")
        
        if self.failed_tests == 0:
            print("\n🎉 ALL TESTS PASSED! Orca OS is ready for VMware testing!")
            return True
        else:
            print(f"\n⚠️  {self.failed_tests} tests failed. Please check the report for details.")
            return False


def main():
    """Main entry point."""
    tester = OrcaSystemTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
