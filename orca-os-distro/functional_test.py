#!/usr/bin/env python3
"""
Orca OS Functional Testing Script
Tests actual functionality with verifiable questions
"""

import subprocess
import sys
import time
import json
from pathlib import Path

def run_orca_test(question, expected_command_patterns=None, expected_output_patterns=None):
    """Run a single Orca test and verify results."""
    print(f"\n🧪 Testing: '{question}'")
    print("=" * 60)
    
    try:
        # Run Orca with auto-confirmation
        cmd = f"cd /Users/nipunkumar/Orca-OS && source venv/bin/activate && echo 'y' | python3 -m orca '{question}'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        
        print(f"Exit Code: {result.returncode}")
        print(f"Output:\n{result.stdout}")
        if result.stderr:
            print(f"Error:\n{result.stderr}")
        
        # Verify results
        success = True
        issues = []
        
        if result.returncode != 0:
            success = False
            issues.append(f"Command failed with exit code {result.returncode}")
        
        # Check if expected command patterns are present
        if expected_command_patterns:
            found_patterns = []
            for pattern in expected_command_patterns:
                if pattern.lower() in result.stdout.lower():
                    found_patterns.append(pattern)
            if not found_patterns:
                success = False
                issues.append(f"Expected command patterns not found: {expected_command_patterns}")
            else:
                print(f"✅ Found expected patterns: {found_patterns}")
        
        # Check if expected output patterns are present
        if expected_output_patterns:
            found_outputs = []
            for pattern in expected_output_patterns:
                if pattern.lower() in result.stdout.lower():
                    found_outputs.append(pattern)
            if not found_outputs:
                success = False
                issues.append(f"Expected output patterns not found: {expected_output_patterns}")
            else:
                print(f"✅ Found expected outputs: {found_outputs}")
        
        return {
            "question": question,
            "success": success,
            "issues": issues,
            "output": result.stdout,
            "error": result.stderr,
            "exit_code": result.returncode
        }
        
    except subprocess.TimeoutExpired:
        return {
            "question": question,
            "success": False,
            "issues": ["Command timed out after 60 seconds"],
            "output": "",
            "error": "Timeout",
            "exit_code": -1
        }
    except Exception as e:
        return {
            "question": question,
            "success": False,
            "issues": [f"Exception: {str(e)}"],
            "output": "",
            "error": str(e),
            "exit_code": -1
        }

def test_system_information():
    """Test system information queries."""
    print("\n🔍 Testing System Information Queries")
    print("=" * 50)
    
    tests = [
        {
            "question": "what is my operating system",
            "expected_command_patterns": ["uname", "system_profiler"],
            "expected_output_patterns": ["darwin", "macos", "system"]
        },
        {
            "question": "show me my CPU information",
            "expected_command_patterns": ["sysctl", "system_profiler"],
            "expected_output_patterns": ["cpu", "processor", "machdep"]
        },
        {
            "question": "what is my current working directory",
            "expected_command_patterns": ["pwd"],
            "expected_output_patterns": ["/Users/nipunkumar/Orca-OS"]
        },
        {
            "question": "show me the current date and time",
            "expected_command_patterns": ["date"],
            "expected_output_patterns": ["2025", "Sep", "September"]
        }
    ]
    
    results = []
    for test in tests:
        result = run_orca_test(
            test["question"],
            test.get("expected_command_patterns"),
            test.get("expected_output_patterns")
        )
        results.append(result)
    
    return results

def test_process_management():
    """Test process management queries."""
    print("\n🔍 Testing Process Management Queries")
    print("=" * 50)
    
    tests = [
        {
            "question": "show me all running processes",
            "expected_command_patterns": ["ps", "aux"],
            "expected_output_patterns": ["PID", "COMMAND", "CPU"]
        },
        {
            "question": "find processes using the most CPU",
            "expected_command_patterns": ["ps", "sort", "cpu"],
            "expected_output_patterns": ["%CPU", "PID"]
        },
        {
            "question": "show me processes with high memory usage",
            "expected_command_patterns": ["ps", "sort", "memory"],
            "expected_output_patterns": ["%MEM", "RSS"]
        }
    ]
    
    results = []
    for test in tests:
        result = run_orca_test(
            test["question"],
            test.get("expected_command_patterns"),
            test.get("expected_output_patterns")
        )
        results.append(result)
    
    return results

def test_file_operations():
    """Test file operation queries."""
    print("\n🔍 Testing File Operation Queries")
    print("=" * 50)
    
    tests = [
        {
            "question": "list all files in the current directory",
            "expected_command_patterns": ["ls", "ls -la"],
            "expected_output_patterns": ["orca", "config", "venv"]
        },
        {
            "question": "show me the size of files in this directory",
            "expected_command_patterns": ["ls", "du", "size"],
            "expected_output_patterns": ["bytes", "KB", "MB"]
        },
        {
            "question": "find all Python files in this directory",
            "expected_command_patterns": ["find", "grep", "*.py"],
            "expected_output_patterns": [".py"]
        }
    ]
    
    results = []
    for test in tests:
        result = run_orca_test(
            test["question"],
            test.get("expected_command_patterns"),
            test.get("expected_output_patterns")
        )
        results.append(result)
    
    return results

def test_network_operations():
    """Test network operation queries."""
    print("\n🔍 Testing Network Operation Queries")
    print("=" * 50)
    
    tests = [
        {
            "question": "show me active network connections",
            "expected_command_patterns": ["netstat", "lsof", "ss"],
            "expected_output_patterns": ["tcp", "udp", "localhost"]
        },
        {
            "question": "check if I can reach google.com",
            "expected_command_patterns": ["ping", "curl", "nc"],
            "expected_output_patterns": ["google", "64 bytes", "time"]
        }
    ]
    
    results = []
    for test in tests:
        result = run_orca_test(
            test["question"],
            test.get("expected_command_patterns"),
            test.get("expected_output_patterns")
        )
        results.append(result)
    
    return results

def test_memory_and_disk():
    """Test memory and disk queries."""
    print("\n🔍 Testing Memory and Disk Queries")
    print("=" * 50)
    
    tests = [
        {
            "question": "show me memory usage",
            "expected_command_patterns": ["vm_stat", "free", "top"],
            "expected_output_patterns": ["memory", "pages", "active", "inactive"]
        },
        {
            "question": "show me disk usage",
            "expected_command_patterns": ["df", "du"],
            "expected_output_patterns": ["Filesystem", "Size", "Used", "Available"]
        },
        {
            "question": "find the largest files on my system",
            "expected_command_patterns": ["find", "du", "sort"],
            "expected_output_patterns": ["MB", "GB", "bytes"]
        }
    ]
    
    results = []
    for test in tests:
        result = run_orca_test(
            test["question"],
            test.get("expected_command_patterns"),
            test.get("expected_output_patterns")
        )
        results.append(result)
    
    return results

def test_advanced_queries():
    """Test advanced AI queries."""
    print("\n🔍 Testing Advanced AI Queries")
    print("=" * 50)
    
    tests = [
        {
            "question": "analyze my system performance and suggest optimizations",
            "expected_command_patterns": ["top", "htop", "iostat"],
            "expected_output_patterns": ["cpu", "memory", "load"]
        },
        {
            "question": "check for any security issues on my system",
            "expected_command_patterns": ["who", "last", "w"],
            "expected_output_patterns": ["users", "login", "security"]
        },
        {
            "question": "show me system logs from the last hour",
            "expected_command_patterns": ["log", "journalctl", "tail"],
            "expected_output_patterns": ["log", "error", "warning"]
        }
    ]
    
    results = []
    for test in tests:
        result = run_orca_test(
            test["question"],
            test.get("expected_command_patterns"),
            test.get("expected_output_patterns")
        )
        results.append(result)
    
    return results

def generate_test_report(all_results):
    """Generate comprehensive test report."""
    print("\n" + "=" * 60)
    print("📊 ORCA OS FUNCTIONAL TEST REPORT")
    print("=" * 60)
    
    total_tests = len(all_results)
    successful_tests = sum(1 for result in all_results if result["success"])
    failed_tests = total_tests - successful_tests
    success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total Tests: {total_tests}")
    print(f"Successful: {successful_tests} ✅")
    print(f"Failed: {failed_tests} ❌")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if failed_tests > 0:
        print("\n❌ Failed Tests:")
        for result in all_results:
            if not result["success"]:
                print(f"  • '{result['question']}'")
                for issue in result["issues"]:
                    print(f"    - {issue}")
    
    print("\n✅ Successful Tests:")
    for result in all_results:
        if result["success"]:
            print(f"  • '{result['question']}'")
    
    # Save detailed report
    report_file = f"functional_test_report_{int(time.time())}.json"
    with open(report_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    print(f"\n📄 Detailed report saved to: {report_file}")
    
    return success_rate >= 80

def main():
    """Run all functional tests."""
    print("🐋 Orca OS Functional Testing Suite")
    print("Testing actual AI functionality with verifiable questions")
    print("=" * 60)
    
    all_results = []
    
    # Run all test categories
    all_results.extend(test_system_information())
    all_results.extend(test_process_management())
    all_results.extend(test_file_operations())
    all_results.extend(test_network_operations())
    all_results.extend(test_memory_and_disk())
    all_results.extend(test_advanced_queries())
    
    # Generate report
    success = generate_test_report(all_results)
    
    if success:
        print("\n🎉 Orca OS functional testing PASSED!")
        print("The AI is working correctly and generating appropriate commands.")
    else:
        print("\n⚠️ Orca OS functional testing FAILED!")
        print("Some issues need to be addressed.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
