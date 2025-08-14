#!/usr/bin/env python3
"""
Test runner for AI_Collab_Teams application
Runs all test suites and provides a comprehensive report
"""

import unittest
import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_all_tests():
    """Run all test suites and return results"""
    # Discover and load all tests
    loader = unittest.TestLoader()
    start_dir = 'tests'
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result

def run_specific_test(test_file):
    """Run a specific test file"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(f'tests.{test_file}')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result

def print_test_summary(result):
    """Print a summary of test results"""
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped) if hasattr(result, 'skipped') else 0
    
    print(f"Total Tests Run: {total_tests}")
    print(f"Failures: {failures}")
    print(f"Errors: {errors}")
    print(f"Skipped: {skipped}")
    print(f"Success Rate: {((total_tests - failures - errors) / total_tests * 100):.1f}%")
    
    if failures > 0:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if errors > 0:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    print("="*60)

def main():
    """Main test runner function"""
    print("AI_Collab_Teams Test Suite")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check if a specific test file was requested
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
        if not test_file.endswith('.py'):
            test_file += '.py'
        print(f"Running specific test: {test_file}")
        result = run_specific_test(test_file)
    else:
        print("Running all tests...")
        result = run_all_tests()
    
    # Print summary
    print_test_summary(result)
    
    # Exit with appropriate code
    if result.failures or result.errors:
        sys.exit(1)
    else:
        print("\n✅ All tests passed!")
        sys.exit(0)

if __name__ == '__main__':
    main() 