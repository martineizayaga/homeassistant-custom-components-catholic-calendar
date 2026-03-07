#!/usr/bin/env python3
import subprocess
import sys
import os

def run_command(command, description):
    print(f"Running {description}...")
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"\n[QUALITY ERROR] {description} failed:")
        print(result.stdout)
        print(result.stderr)
        return False
    return True

def main():
    target = "custom_components/catholic_calendar"
    git_bin = "/usr/bin/git"

    # 1. Formatting & Linting with Ruff (Auto-fix)
    if not run_command(["./venv/bin/ruff", "check", "--fix", target], "Ruff Linting"):
        sys.exit(1)
    
    if not run_command(["./venv/bin/ruff", "format", target], "Ruff Formatting"):
        sys.exit(1)

    # SENIOR SAFETY: Re-stage files if Ruff changed them
    # This ensures the fixed versions are actually committed
    subprocess.run([git_bin, "add", target])

    # 2. Static Analysis with Mypy
    # Note: Mypy is read-only and will only report errors
    if not run_command(["./venv/bin/mypy", target], "Mypy Type Checking"):
        sys.exit(1)

    print("\n✅ Quality checks passed!")
    sys.exit(0)

if __name__ == "__main__":
    main()
