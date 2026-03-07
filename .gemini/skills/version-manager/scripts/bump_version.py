import json
import os
import re
import sys


def update_file(filepath, pattern, replacement):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return False
    with open(filepath) as f:
        content = f.read()
    new_content = re.sub(pattern, replacement, content)
    if new_content == content:
        print(
            f"Warning: No changes made to {filepath}. Pattern might not have matched."
        )
    with open(filepath, "w") as f:
        f.write(new_content)
    print(f"Updated {filepath}")
    return True


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 bump_version.py <new_version>")
        sys.exit(1)

    new_version = sys.argv[1]

    # 1. Update pyproject.toml
    update_file(
        "pyproject.toml", r'version\s*=\s*"[^"]+"', f'version = "{new_version}"'
    )

    # 2. Update manifest.json
    try:
        with open("custom_components/catholic_calendar/manifest.json") as f:
            manifest = json.load(f)
        manifest["version"] = new_version
        with open("custom_components/catholic_calendar/manifest.json", "w") as f:
            json.dump(manifest, f, indent=2)
            f.write("\n")  # Add trailing newline
        print("Updated custom_components/catholic_calendar/manifest.json")
    except Exception as e:
        print(f"Failed to update manifest.json: {e}")

    # 3. Update sensor.py
    update_file(
        "custom_components/catholic_calendar/sensor.py",
        r'__version__\s*=\s*"[^"]+"',
        f'__version__ = "{new_version}"',
    )

    # 4. Update calendar.py
    update_file(
        "custom_components/catholic_calendar/calendar.py",
        r'__version__\s*=\s*"[^"]+"',
        f'__version__ = "{new_version}"',
    )

    print(f"\nSuccessfully bumped version to {new_version} across all files.")


if __name__ == "__main__":
    main()
