#!/usr/bin/env python3
import json
import subprocess
import sys


def get_staged_files():
    # Use absolute path to git to resolve security/linting warnings
    result = subprocess.run(  # noqa: S603
        ["/usr/bin/git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.splitlines()


def get_current_version():
    try:
        with open("custom_components/catholic_calendar/manifest.json") as f:
            manifest = json.load(f)
        return manifest.get("version", "0.0.0")
    except FileNotFoundError, json.JSONDecodeError:
        return "0.0.0"


def calculate_next_versions(current_version):
    # Senior: Strip any pre-release or build metadata (e.g., 2.0.1-beta -> 2.0.1)
    base_version = current_version.split("-")[0].split("+")[0]
    parts = base_version.split(".")

    # Skeptical: Pad with zeros if version is short (e.g., "2.0" -> ["2", "0", "0"])
    while len(parts) < 3:
        parts.append("0")

    try:
        # Idiomatic: Only take the first 3 numeric parts
        major, minor, patch = map(int, parts[:3])
        return {
            "patch": f"{major}.{minor}.{patch + 1}",
            "minor": f"{major}.{minor + 1}.0",
            "major": f"{major + 1}.0.0",
        }
    except ValueError:
        # Skeptical: If it's not numbers, we can't safely bump it
        return {}


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

    # If logic changed but version didn't, interact or block
    if logic_files and not version_changed:
        print("\n[PRE-COMMIT] Logic changes detected, but no version bump found.")

        # Senior: Git hooks often redirect stdin. Use /dev/tty for interactive input.
        is_interactive = sys.stdin.isatty() or sys.stderr.isatty()
        if not is_interactive:
            print("\nNon-interactive environment detected. Please bump manually.")
            sys.exit(1)

        current = get_current_version()
        next_v = calculate_next_versions(current)

        if not next_v:
            print(f"Failed to parse current version: {current}")
            sys.exit(1)

        print(f"\nCurrent version is: {current}")
        print("Would you like to bump the version now?")
        print(f"  1) Patch: {next_v['patch']}")
        print(f"  2) Minor: {next_v['minor']}")
        print(f"  3) Major: {next_v['major']}")
        print("  n) No, I will do it later (Aborts commit)")

        try:
            # Senior: Try reading from /dev/tty to bypass stdin redirection
            with open("/dev/tty") as tty:
                print("\nSelect an option [1, 2, 3, n]: ", end="", flush=True)
                choice = tty.readline().strip().lower()
        except OSError:
            # Fallback to standard input
            choice = input("\nSelect an option [1, 2, 3, n]: ").strip().lower()

        bump_to = None
        if choice == "1":
            bump_to = next_v["patch"]
        elif choice == "2":
            bump_to = next_v["minor"]
        elif choice == "3":
            bump_to = next_v["major"]

        if bump_to:
            print(f"\nBumping version to {bump_to}...")
            # Call the bump script
            bump_script = ".gemini/skills/version-manager/scripts/bump_version.py"
            subprocess.run([sys.executable, bump_script, bump_to], check=True)  # noqa: S603

            # Re-stage version files
            print("Staging updated version files...")
            subprocess.run(["/usr/bin/git", "add"] + version_files, check=True)  # noqa: S603
            print("\n✅ Version bumped and staged! Proceeding with commit...")
            sys.exit(0)
        else:
            print("\nCommit aborted. Please bump version before committing.")
            sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
