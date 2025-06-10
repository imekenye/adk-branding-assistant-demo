"""
Quality assurance and environment validation script
"""

import subprocess
import sys
from pathlib import Path


def run_quality_checks():
    """Run comprehensive quality checks"""

    print("🔍 Running quality assurance checks...")

    # Code formatting
    print("📝 Checking code formatting...")
    subprocess.run(["uv", "run", "black", "--check", "."], check=False)

    # Import sorting
    print("📋 Checking import organization...")
    subprocess.run(["uv", "run", "isort", "--check-only", "."], check=False)

    # Type checking
    print("🔍 Running type checks...")
    subprocess.run(["uv", "run", "mypy", "agents/", "tools/"], check=False)

    # Security check (basic)
    print("🔒 Checking for common security issues...")
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file) as f:
            content = f.read()
            if "your-" in content:
                print("⚠️  Warning: .env file contains placeholder values")

    print("✅ Quality checks complete!")


if __name__ == "__main__":
    run_quality_checks()
