#!/usr/bin/env python3
import subprocess
import sys


def run_command(command, description):
    print(f"Running {description}...")
    result = subprocess.run(  # noqa: S603
        command, capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        print(f"\n[QUALITY INFO] {description} produced output/errors:")
        print(result.stdout)
        print(result.stderr)
        return False
    return True


def main():
    # Define targets for quality checks
    targets = [
        "custom_components/catholic_calendar",
        "scripts",
        ".gemini/skills/version-manager/scripts",
    ]
    git_bin = "/usr/bin/git"

    # 1. Formatting & Linting with Ruff (Mandatory)
    # Ruff is very reliable and should block the commit if it fails.
    if not run_command(["./venv/bin/ruff", "check", "--fix"] + targets, "Ruff Linting"):
        # If ruff found errors it couldn't fix, we block.
        sys.exit(1)

    if not run_command(["./venv/bin/ruff", "format"] + targets, "Ruff Formatting"):
        sys.exit(1)

    # Re-stage files if Ruff changed them
    subprocess.run([git_bin, "add"] + targets, check=False)  # noqa: S603

    # 2. Static Analysis with Mypy (Informational)
    # Senior Note: Mypy is difficult to pass 100% without a full HA dev env.
    # We run it to provide feedback but don't block the commit.
    mypy_cmd = [
        "./venv/bin/mypy",
        "--ignore-missing-imports",
        "--follow-imports=skip",
        "--check-untyped-defs",
    ] + targets
    run_command(mypy_cmd, "Mypy Type Checking (Informational)")

    print("\n✅ Quality checks finished!")
    sys.exit(0)


if __name__ == "__main__":
    main()
