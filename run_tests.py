#!/usr/bin/env python3
"""
Test runner script for RBAC Auth System.
Provides various options for running different test suites.
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle the result"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"\n✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"\n❌ Command not found. Make sure pytest is installed.")
        return False


def main():
    parser = argparse.ArgumentParser(description="Run RBAC Auth System tests")
    parser.add_argument(
        "--suite", 
        choices=["all", "unit", "integration", "auth", "permissions", "models", "fast"],
        default="all",
        help="Test suite to run"
    )
    parser.add_argument(
        "--coverage", 
        action="store_true",
        help="Run tests with coverage report"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--failfast", "-x",
        action="store_true",
        help="Stop on first failure"
    )
    parser.add_argument(
        "--parallel", "-n",
        type=int,
        help="Run tests in parallel (requires pytest-xdist)"
    )
    
    args = parser.parse_args()
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add verbosity
    if args.verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")
    
    # Add fail fast
    if args.failfast:
        cmd.append("-x")
    
    # Add parallel execution
    if args.parallel:
        cmd.extend(["-n", str(args.parallel)])
    
    # Add coverage
    if args.coverage:
        cmd.extend([
            "--cov=app",
            "--cov-report=html",
            "--cov-report=term-missing",
            "--cov-fail-under=80"
        ])
    
    # Select test suite
    if args.suite == "all":
        cmd.append("tests/")
        description = "All tests"
    elif args.suite == "unit":
        cmd.extend([
            "tests/test_models.py",
            "tests/test_permissions.py", 
            "tests/test_auth_utils.py"
        ])
        description = "Unit tests"
    elif args.suite == "integration":
        cmd.append("tests/test_integration.py")
        description = "Integration tests"
    elif args.suite == "auth":
        cmd.extend([
            "tests/test_auth.py",
            "tests/test_auth_utils.py"
        ])
        description = "Authentication tests"
    elif args.suite == "permissions":
        cmd.extend([
            "tests/test_permissions.py",
            "tests/test_protected_routes.py"
        ])
        description = "Permission tests"
    elif args.suite == "models":
        cmd.append("tests/test_models.py")
        description = "Model tests"
    elif args.suite == "fast":
        cmd.extend([
            "tests/test_models.py",
            "tests/test_permissions.py",
            "tests/test_auth_utils.py",
            "-m", "not slow"
        ])
        description = "Fast tests (excluding slow tests)"
    
    # Run the tests
    success = run_command(cmd, description)
    
    if success:
        print(f"\n🎉 Test suite '{args.suite}' passed!")
        if args.coverage:
            print("\n📊 Coverage report generated in htmlcov/index.html")
    else:
        print(f"\n💥 Test suite '{args.suite}' failed!")
        sys.exit(1)


if __name__ == "__main__":
    # Check if we're in the right directory
    if not Path("app").exists() or not Path("tests").exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    main()