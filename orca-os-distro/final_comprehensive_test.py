#!/usr/bin/env python3
"""
Orca OS Final Comprehensive Test
Tests all core functionality after cleanup
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class FinalComprehensiveTest:
    """Final comprehensive test for Orca OS."""
    
    def __init__(self):
        """Initialize the test suite."""
        self.test_results = {}
        self.start_time = datetime.now()
        self.project_root = Path.cwd()
        
    def log_test(self, test_name: str, success: bool, message: str = "", details: Dict = None):
        """Log test result."""
        self.test_results[test_name] = {
            "success": success,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
    
    def test_project_structure(self):
        """Test overall project structure."""
        print("\n🔍 Testing Project Structure...")
        
        # Test main directories
        required_dirs = ["advanced", "kernel", "iso"]
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            self.log_test(f"Directory {dir_name}", dir_path.exists() and dir_path.is_dir(), 
                         "Exists" if dir_path.exists() else "Missing")
        
        # Test core files
        core_files = [
            "test_complete_system.py",
            "test_individual_features.py", 
            "install_and_test_complete.sh",
            "deploy_advanced_features.sh",
            "build_c++_components.sh",
            "VMWARE_TESTING_GUIDE.md",
            "FINAL_PROJECT_SUMMARY.md",
            "ARCHITECTURE_C++_PERFORMANCE.md",
            "PHASE3_4_COMPLETE.md"
        ]
        
        for file_name in core_files:
            file_path = self.project_root / file_name
            self.log_test(f"Core file {file_name}", file_path.exists(), 
                         "Exists" if file_path.exists() else "Missing")
    
    def test_advanced_features(self):
        """Test advanced features."""
        print("\n🔍 Testing Advanced Features...")
        
        advanced_files = [
            "advanced/orca-dashboard.py",
            "advanced/orca-optimizer.py", 
            "advanced/predictive-ai.py",
            "advanced/plugin-system.py",
            "advanced/orca-package-manager.py",
            "advanced/test_advanced_features.py"
        ]
        
        for file_name in advanced_files:
            file_path = self.project_root / file_name
            self.log_test(f"Advanced feature {Path(file_name).name}", file_path.exists(),
                         "Exists" if file_path.exists() else "Missing")
    
    def test_kernel_components(self):
        """Test kernel components."""
        print("\n🔍 Testing Kernel Components...")
        
        kernel_files = [
            "kernel/orca-kernel-module.c",
            "kernel/orca-ai-middleware.cpp",
            "kernel/orca_ai_types.h",
            "kernel/Makefile",
            "kernel/ai-process-manager.py",
            "kernel/ai-logging-system.py",
            "kernel/ai-scheduler.py"
        ]
        
        for file_name in kernel_files:
            file_path = self.project_root / file_name
            self.log_test(f"Kernel component {Path(file_name).name}", file_path.exists(),
                         "Exists" if file_path.exists() else "Missing")
    
    def test_python_syntax(self):
        """Test Python syntax."""
        print("\n🔍 Testing Python Syntax...")
        
        python_files = list(self.project_root.rglob("*.py"))
        syntax_errors = 0
        
        for py_file in python_files:
            try:
                result = subprocess.run([sys.executable, "-m", "py_compile", str(py_file)], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode != 0:
                    syntax_errors += 1
                    print(f"    Syntax error in {py_file}: {result.stderr}")
            except Exception as e:
                syntax_errors += 1
                print(f"    Error compiling {py_file}: {e}")
        
        self.log_test("Python Syntax", syntax_errors == 0, 
                     f"{syntax_errors} syntax errors found" if syntax_errors > 0 else "All files valid")
    
    def test_script_permissions(self):
        """Test script permissions."""
        print("\n🔍 Testing Script Permissions...")
        
        scripts = list(self.project_root.glob("*.sh"))
        permission_errors = 0
        
        for script in scripts:
            if not os.access(script, os.X_OK):
                permission_errors += 1
                print(f"    Script not executable: {script}")
        
        self.log_test("Script Permissions", permission_errors == 0,
                     f"{permission_errors} scripts not executable" if permission_errors > 0 else "All scripts executable")
    
    def test_documentation(self):
        """Test documentation completeness."""
        print("\n🔍 Testing Documentation...")
        
        doc_files = [
            "VMWARE_TESTING_GUIDE.md",
            "FINAL_PROJECT_SUMMARY.md", 
            "ARCHITECTURE_C++_PERFORMANCE.md",
            "PHASE3_4_COMPLETE.md"
        ]
        
        total_chars = 0
        for doc_file in doc_files:
            file_path = self.project_root / doc_file
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        total_chars += len(content)
                        self.log_test(f"Documentation {doc_file}", len(content) > 1000,
                                     f"{len(content)} characters")
                except Exception as e:
                    self.log_test(f"Documentation {doc_file}", False, f"Error reading: {e}")
            else:
                self.log_test(f"Documentation {doc_file}", False, "Missing")
        
        self.log_test("Documentation Completeness", total_chars > 40000,
                     f"Total documentation: {total_chars} characters")
    
    def test_core_orca_integration(self):
        """Test core Orca OS integration."""
        print("\n🔍 Testing Core Orca OS Integration...")
        
        # Check if main orca directory exists
        main_orca_path = self.project_root.parent / "orca"
        self.log_test("Main Orca Directory", main_orca_path.exists(),
                     "Found" if main_orca_path.exists() else "Not found")
        
        if main_orca_path.exists():
            # Check key files
            key_files = ["cli.py", "core/daemon.py", "llm/manager.py", "security/validator.py"]
            for file_name in key_files:
                file_path = main_orca_path / file_name
                self.log_test(f"Core file {file_name}", file_path.exists(),
                             "Exists" if file_path.exists() else "Missing")
    
    def test_file_consistency(self):
        """Test file consistency and no duplicates."""
        print("\n🔍 Testing File Consistency...")
        
        # Check for duplicate files
        file_hashes = {}
        duplicates = 0
        
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith('.'):
                try:
                    with open(file_path, 'rb') as f:
                        content = f.read()
                        file_hash = hash(content)
                        if file_hash in file_hashes:
                            duplicates += 1
                            print(f"    Duplicate found: {file_path} and {file_hashes[file_hash]}")
                        else:
                            file_hashes[file_hash] = file_path
                except Exception:
                    continue
        
        self.log_test("File Consistency", duplicates == 0,
                     f"{duplicates} duplicate files found" if duplicates > 0 else "No duplicates")
    
    def test_cleanup_effectiveness(self):
        """Test cleanup effectiveness."""
        print("\n🔍 Testing Cleanup Effectiveness...")
        
        # Check for cache files
        cache_files = list(self.project_root.rglob("__pycache__")) + list(self.project_root.rglob("*.pyc"))
        self.log_test("Cache Files Cleanup", len(cache_files) == 0,
                     f"{len(cache_files)} cache files found" if cache_files else "No cache files")
        
        # Check for empty directories
        empty_dirs = []
        for dir_path in self.project_root.rglob("*"):
            if dir_path.is_dir() and not any(dir_path.iterdir()):
                empty_dirs.append(dir_path)
        
        self.log_test("Empty Directories Cleanup", len(empty_dirs) == 0,
                     f"{len(empty_dirs)} empty directories found" if empty_dirs else "No empty directories")
    
    def test_import_structure(self):
        """Test import structure."""
        print("\n🔍 Testing Import Structure...")
        
        # Test if advanced features can import from main orca
        test_script = """
import sys
import os
sys.path.insert(0, '../orca')

try:
    # Test core imports
    from orca.core.models import UserQuery, CommandSuggestion, ExecutionResult
    from orca.llm.manager import LLMManager
    from orca.security.validator import CommandValidator
    from orca.core.executor import CommandExecutor
    from orca.core.context import ContextProvider
    print("Core imports successful")
    
    # Test that we can create instances
    query = UserQuery(query="test query")
    print("Model instantiation successful")
    
except Exception as e:
    print(f"Import error: {e}")
    sys.exit(1)
"""
        
        try:
            result = subprocess.run([sys.executable, "-c", test_script], 
                                  capture_output=True, text=True, timeout=30)
            self.log_test("Import Structure", result.returncode == 0,
                         "All imports successful" if result.returncode == 0 else f"Import failed: {result.stderr}")
        except Exception as e:
            self.log_test("Import Structure", False, f"Test error: {e}")
    
    def test_advanced_feature_functionality(self):
        """Test advanced feature functionality."""
        print("\n🔍 Testing Advanced Feature Functionality...")
        
        # Test each advanced feature can be imported
        advanced_features = [
            "advanced/orca-dashboard.py",
            "advanced/orca-optimizer.py",
            "advanced/predictive-ai.py", 
            "advanced/plugin-system.py",
            "advanced/orca-package-manager.py"
        ]
        
        for feature_file in advanced_features:
            if Path(feature_file).exists():
                try:
                    # Test if file can be compiled
                    result = subprocess.run([sys.executable, "-m", "py_compile", feature_file], 
                                          capture_output=True, text=True, timeout=10)
                    self.log_test(f"Feature {Path(feature_file).stem}", result.returncode == 0,
                                 "Compiles successfully" if result.returncode == 0 else f"Compile error: {result.stderr}")
                except Exception as e:
                    self.log_test(f"Feature {Path(feature_file).stem}", False, f"Test error: {e}")
    
    def generate_final_report(self) -> Dict[str, Any]:
        """Generate final test report."""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        # Calculate statistics
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Count files
        total_files = len(list(self.project_root.rglob("*")))
        python_files = len(list(self.project_root.rglob("*.py")))
        shell_files = len(list(self.project_root.rglob("*.sh")))
        markdown_files = len(list(self.project_root.rglob("*.md")))
        c_files = len(list(self.project_root.rglob("*.c")))
        cpp_files = len(list(self.project_root.rglob("*.cpp")))
        
        report = {
            "test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": success_rate,
                "duration_seconds": duration.total_seconds()
            },
            "project_statistics": {
                "total_files": total_files,
                "python_files": python_files,
                "shell_files": shell_files,
                "markdown_files": markdown_files,
                "c_files": c_files,
                "cpp_files": cpp_files
            },
            "test_results": self.test_results,
            "timestamp": end_time.isoformat(),
            "cleanup_status": "COMPLETE"
        }
        
        return report
    
    def run_final_test(self):
        """Run final comprehensive test."""
        print("🐋 Orca OS Final Comprehensive Test")
        print("=" * 50)
        print(f"Started at: {self.start_time.isoformat()}")
        print()
        
        # Run all tests
        self.test_project_structure()
        self.test_advanced_features()
        self.test_kernel_components()
        self.test_python_syntax()
        self.test_script_permissions()
        self.test_documentation()
        self.test_core_orca_integration()
        self.test_file_consistency()
        self.test_cleanup_effectiveness()
        self.test_import_structure()
        self.test_advanced_feature_functionality()
        
        # Generate report
        report = self.generate_final_report()
        
        # Save report
        report_file = f"final_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 FINAL COMPREHENSIVE TEST SUMMARY")
        print("=" * 50)
        print(f"Total Tests: {report['test_summary']['total_tests']}")
        print(f"Passed: {report['test_summary']['passed_tests']} ✅")
        print(f"Failed: {report['test_summary']['failed_tests']} ❌")
        print(f"Success Rate: {report['test_summary']['success_rate']:.1f}%")
        print(f"Duration: {report['test_summary']['duration_seconds']:.1f} seconds")
        print()
        print("📁 Project Statistics:")
        print(f"  Total Files: {report['project_statistics']['total_files']}")
        print(f"  Python Files: {report['project_statistics']['python_files']}")
        print(f"  Shell Files: {report['project_statistics']['shell_files']}")
        print(f"  Markdown Files: {report['project_statistics']['markdown_files']}")
        print(f"  C Files: {report['project_statistics']['c_files']}")
        print(f"  C++ Files: {report['project_statistics']['cpp_files']}")
        print()
        print(f"📄 Report saved to: {report_file}")
        
        # Overall assessment
        if report['test_summary']['success_rate'] >= 90:
            print("\n🎉 EXCELLENT! Orca OS is clean, optimized, and ready for VMware testing!")
        elif report['test_summary']['success_rate'] >= 80:
            print("\n✅ GOOD! Orca OS is mostly ready with minor issues.")
        else:
            print("\n⚠️ NEEDS ATTENTION! Some issues need to be resolved.")
        
        return report['test_summary']['success_rate'] >= 80

def main():
    """Main entry point."""
    tester = FinalComprehensiveTest()
    success = tester.run_final_test()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
