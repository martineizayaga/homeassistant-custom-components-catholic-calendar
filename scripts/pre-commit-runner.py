#!/usr/bin/env python3
import subprocess
import sys


def main():
    # List of scripts to run
    # We use absolute paths relative to the project root for stability
    scripts = ["scripts/pre-commit-quality.py", "scripts/pre-commit-version.py"]

    for script in scripts:
        # Run each script using the same interpreter
        result = subprocess.run([sys.executable, script])  # noqa: S603
        if result.returncode != 0:
            sys.exit(result.returncode)

    sys.exit(0)


if __name__ == "__main__":
    main()
