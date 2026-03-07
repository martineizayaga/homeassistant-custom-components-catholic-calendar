#!/usr/bin/env python3
import subprocess
import sys


def get_staged_files():
    # Use absolute path to git to resolve security/linting warnings
    result = subprocess.run(
        ["/usr/bin/git", "diff", "--cached", "--name-only"], capture_output=True, text=True
    )
    return result.stdout.splitlines()


def main():
    staged_files = get_staged_files()

    # Files that define the integration logic
    logic_files = [
        f
        for f in staged_files
        if f.startswith("custom_components/catholic_calendar/") and f.endswith(".py")
    ]

    # Files that hold the version string
    version_files = [
        "custom_components/catholic_calendar/manifest.json",
        "pyproject.toml",
        "custom_components/catholic_calendar/sensor.py",
        "custom_components/catholic_calendar/calendar.py",
    ]

    version_changed = any(f in staged_files for f in version_files)

    # If logic changed but version didn't, warn or block
    if logic_files and not version_changed:
        print("\n[PRE-COMMIT ERROR] Logic changes detected in:")
        for f in logic_files:
            print(f"  - {f}")
        print(
            "\nBut no version files were updated. Please bump the version before committing."
        )
        print("Tip: Ask Gemini to 'Update the version strings based on my changes.'")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
