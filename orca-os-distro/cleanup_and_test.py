#!/usr/bin/env python3
"""
Orca OS Cleanup and Testing Script
Analyzes codebase, removes unnecessary files, and runs comprehensive tests
"""

import os
import sys
import shutil
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set, Tuple

class OrcaCleanupAndTest:
    """Comprehensive cleanup and testing for Orca OS."""
    
    def __init__(self):
        """Initialize the cleanup and test system."""
        self.project_root = Path.cwd()
        self.cleanup_log = []
        self.test_results = {}
        self.start_time = datetime.now()
        
    def log_action(self, action: str, details: str = ""):
        """Log cleanup action."""
        self.cleanup_log.append({
            "action": action,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        print(f"🧹 {action}: {details}")
    
    def analyze_codebase(self) -> Dict[str, List[str]]:
        """Analyze the codebase structure."""
        print("\n🔍 Analyzing Codebase Structure...")
        
        analysis = {
            "duplicate_files": [],
            "unused_files": [],
            "cache_files": [],
            "empty_directories": [],
            "redundant_directories": []
        }
        
        # Find duplicate files
        file_hashes = {}
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith('.'):
                try:
                    with open(file_path, 'rb') as f:
                        content = f.read()
                        file_hash = hash(content)
                        if file_hash in file_hashes:
                            analysis["duplicate_files"].append({
                                "original": str(file_hashes[file_hash]),
                                "duplicate": str(file_path)
                            })
                        else:
                            file_hashes[file_hash] = file_path
                except Exception as e:
                    print(f"Warning: Could not analyze {file_path}: {e}")
        
        # Find cache files
        for cache_dir in self.project_root.rglob("__pycache__"):
            if cache_dir.is_dir():
                analysis["cache_files"].append(str(cache_dir))
        
        for pyc_file in self.project_root.rglob("*.pyc"):
            analysis["cache_files"].append(str(pyc_file))
        
        # Find empty directories
        for dir_path in self.project_root.rglob("*"):
            if dir_path.is_dir() and not any(dir_path.iterdir()):
                analysis["empty_directories"].append(str(dir_path))
        
        # Check for redundant directories
        if (self.project_root / "orca-core").exists() and (self.project_root.parent / "orca").exists():
            analysis["redundant_directories"].append("orca-core (duplicate of ../orca)")
        
        return analysis
    
    def cleanup_cache_files(self) -> int:
        """Remove Python cache files."""
        print("\n🧹 Cleaning Cache Files...")
        
        removed_count = 0
        
        # Remove __pycache__ directories
        for cache_dir in self.project_root.rglob("__pycache__"):
            if cache_dir.is_dir():
                try:
                    shutil.rmtree(cache_dir)
                    self.log_action("Removed cache directory", str(cache_dir))
                    removed_count += 1
                except Exception as e:
                    self.log_action("Failed to remove cache directory", f"{cache_dir}: {e}")
        
        # Remove .pyc files
        for pyc_file in self.project_root.rglob("*.pyc"):
            try:
                pyc_file.unlink()
                self.log_action("Removed .pyc file", str(pyc_file))
                removed_count += 1
            except Exception as e:
                self.log_action("Failed to remove .pyc file", f"{pyc_file}: {e}")
        
        return removed_count
    
    def cleanup_duplicate_files(self, duplicates: List[Dict]) -> int:
        """Remove duplicate files."""
        print("\n🧹 Cleaning Duplicate Files...")
        
        removed_count = 0
        
        for duplicate in duplicates:
            duplicate_path = Path(duplicate["duplicate"])
            original_path = Path(duplicate["original"])
            
            # Keep the one in the main orca directory, remove others
            if "orca-core" in str(duplicate_path) and "orca-core" not in str(original_path):
                try:
                    duplicate_path.unlink()
                    self.log_action("Removed duplicate file", f"{duplicate_path} (kept {original_path})")
                    removed_count += 1
                except Exception as e:
                    self.log_action("Failed to remove duplicate", f"{duplicate_path}: {e}")
        
        return removed_count
    
    def cleanup_redundant_directories(self) -> int:
        """Remove redundant directories."""
        print("\n🧹 Cleaning Redundant Directories...")
        
        removed_count = 0
        
        # Remove orca-core if it's a duplicate of ../orca
        orca_core_path = self.project_root / "orca-core"
        main_orca_path = self.project_root.parent / "orca"
        
        if orca_core_path.exists() and main_orca_path.exists():
            try:
                # Compare directory contents
                orca_core_files = set(f.name for f in orca_core_path.rglob("*") if f.is_file())
                main_orca_files = set(f.name for f in main_orca_path.rglob("*") if f.is_file())
                
                if orca_core_files.issubset(main_orca_files):
                    shutil.rmtree(orca_core_path)
                    self.log_action("Removed redundant directory", "orca-core (duplicate of ../orca)")
                    removed_count += 1
                else:
                    self.log_action("Skipped orca-core removal", "Contains unique files")
            except Exception as e:
                self.log_action("Failed to remove orca-core", str(e))
        
        return removed_count
    
    def cleanup_empty_directories(self, empty_dirs: List[str]) -> int:
        """Remove empty directories."""
        print("\n🧹 Cleaning Empty Directories...")
        
        removed_count = 0
        
        for empty_dir in empty_dirs:
            try:
                Path(empty_dir).rmdir()
                self.log_action("Removed empty directory", empty_dir)
                removed_count += 1
            except Exception as e:
                self.log_action("Failed to remove empty directory", f"{empty_dir}: {e}")
        
        return removed_count
    
    def identify_unused_files(self) -> List[str]:
        """Identify potentially unused files."""
        print("\n🔍 Identifying Unused Files...")
        
        unused_files = []
        
        # Files that might be unused
        potentially_unused = [
            "packages/orca-package-manager.py",  # Duplicate of advanced version
            "desktop/orca-gnome-extension.py",   # Not integrated
            "installer/orca-installer.py",       # Not integrated
            "scripts/shell-integration.sh",      # Not integrated
            "integrate_advanced_features.sh",    # Superseded by deploy script
            "build_orca_os.sh",                  # Superseded by install script
        ]
        
        for file_path in potentially_unused:
            full_path = self.project_root / file_path
            if full_path.exists():
                # Check if file is referenced anywhere
                is_referenced = False
                for py_file in self.project_root.rglob("*.py"):
                    try:
                        with open(py_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if file_path in content or full_path.name in content:
                                is_referenced = True
                                break
                    except Exception:
                        continue
                
                if not is_referenced:
                    unused_files.append(str(full_path))
        
        return unused_files
    
    def cleanup_unused_files(self, unused_files: List[str]) -> int:
        """Remove unused files."""
        print("\n🧹 Cleaning Unused Files...")
        
        removed_count = 0
        
        for file_path in unused_files:
            try:
                Path(file_path).unlink()
                self.log_action("Removed unused file", file_path)
                removed_count += 1
            except Exception as e:
                self.log_action("Failed to remove unused file", f"{file_path}: {e}")
        
        return removed_count
    
    def run_comprehensive_tests(self) -> Dict[str, bool]:
        """Run comprehensive tests."""
        print("\n🧪 Running Comprehensive Tests...")
        
        test_results = {}
        
        # Test 1: File structure integrity
        print("  Testing file structure integrity...")
        try:
            result = subprocess.run([sys.executable, "simple_test.py"], 
                                  capture_output=True, text=True, timeout=60)
            test_results["file_structure"] = result.returncode == 0
            if result.returncode != 0:
                print(f"    File structure test failed: {result.stderr}")
        except Exception as e:
            test_results["file_structure"] = False
            print(f"    File structure test error: {e}")
        
        # Test 2: Python syntax validation
        print("  Testing Python syntax...")
        try:
            python_files = list(self.project_root.rglob("*.py"))
            syntax_errors = 0
            for py_file in python_files:
                result = subprocess.run([sys.executable, "-m", "py_compile", str(py_file)], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode != 0:
                    syntax_errors += 1
                    print(f"    Syntax error in {py_file}: {result.stderr}")
            
            test_results["python_syntax"] = syntax_errors == 0
        except Exception as e:
            test_results["python_syntax"] = False
            print(f"    Python syntax test error: {e}")
        
        # Test 3: Import validation
        print("  Testing import validation...")
        try:
            # Test main orca imports
            test_script = """
import sys
sys.path.insert(0, '../orca')
try:
    from orca.core.models import UserQuery, CommandSuggestion
    from orca.llm.manager import LLMManager
    from orca.security.validator import CommandValidator
    print("Core imports successful")
except Exception as e:
    print(f"Import error: {e}")
    sys.exit(1)
"""
            result = subprocess.run([sys.executable, "-c", test_script], 
                                  capture_output=True, text=True, timeout=30)
            test_results["import_validation"] = result.returncode == 0
            if result.returncode != 0:
                print(f"    Import validation failed: {result.stderr}")
        except Exception as e:
            test_results["import_validation"] = False
            print(f"    Import validation error: {e}")
        
        # Test 4: Script permissions
        print("  Testing script permissions...")
        try:
            scripts = list(self.project_root.glob("*.sh"))
            permission_errors = 0
            for script in scripts:
                if not os.access(script, os.X_OK):
                    permission_errors += 1
                    print(f"    Script not executable: {script}")
            
            test_results["script_permissions"] = permission_errors == 0
        except Exception as e:
            test_results["script_permissions"] = False
            print(f"    Script permissions test error: {e}")
        
        return test_results
    
    def generate_cleanup_report(self) -> Dict[str, any]:
        """Generate cleanup report."""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        # Count files before and after
        files_before = len(list(self.project_root.rglob("*")))
        files_after = len([f for f in self.project_root.rglob("*") if f.is_file()])
        
        report = {
            "cleanup_summary": {
                "duration_seconds": duration.total_seconds(),
                "files_removed": len(self.cleanup_log),
                "actions_taken": [log["action"] for log in self.cleanup_log]
            },
            "cleanup_log": self.cleanup_log,
            "test_results": self.test_results,
            "timestamp": end_time.isoformat()
        }
        
        return report
    
    def run_cleanup_and_test(self):
        """Run complete cleanup and testing process."""
        print("🐋 Orca OS Cleanup and Testing Suite")
        print("=" * 50)
        print(f"Started at: {self.start_time.isoformat()}")
        print()
        
        # Step 1: Analyze codebase
        analysis = self.analyze_codebase()
        
        # Step 2: Cleanup cache files
        cache_removed = self.cleanup_cache_files()
        
        # Step 3: Cleanup duplicate files
        duplicates_removed = self.cleanup_duplicate_files(analysis["duplicate_files"])
        
        # Step 4: Cleanup redundant directories
        dirs_removed = self.cleanup_redundant_directories()
        
        # Step 5: Cleanup empty directories
        empty_dirs_removed = self.cleanup_empty_directories(analysis["empty_directories"])
        
        # Step 6: Identify and cleanup unused files
        unused_files = self.identify_unused_files()
        unused_removed = self.cleanup_unused_files(unused_files)
        
        # Step 7: Run comprehensive tests
        self.test_results = self.run_comprehensive_tests()
        
        # Step 8: Generate report
        report = self.generate_cleanup_report()
        
        # Save report
        report_file = f"cleanup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 CLEANUP AND TEST SUMMARY")
        print("=" * 50)
        print(f"Cache files removed: {cache_removed}")
        print(f"Duplicate files removed: {duplicates_removed}")
        print(f"Redundant directories removed: {dirs_removed}")
        print(f"Empty directories removed: {empty_dirs_removed}")
        print(f"Unused files removed: {unused_removed}")
        print(f"Total cleanup actions: {len(self.cleanup_log)}")
        print()
        print("🧪 Test Results:")
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {test_name}: {status}")
        
        print(f"\n📄 Report saved to: {report_file}")
        
        # Overall success
        all_tests_passed = all(self.test_results.values())
        if all_tests_passed:
            print("\n🎉 All tests passed! Orca OS is clean and ready!")
        else:
            print("\n⚠️ Some tests failed. Check the report for details.")
        
        return all_tests_passed

def main():
    """Main entry point."""
    cleaner = OrcaCleanupAndTest()
    success = cleaner.run_cleanup_and_test()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
