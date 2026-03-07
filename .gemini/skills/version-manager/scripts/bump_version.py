import argparse
import json
import os
import re


def update_file(filepath, pattern, replacement, dry_run=False):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return False

    with open(filepath) as f:
        content = f.read()

    match = re.search(pattern, content, flags=re.MULTILINE)
    if not match:
        print(f"Warning: No version match found in {filepath}.")
        return False

    old_version_line = match.group(0)
    new_version_line = replacement

    if new_version_line == old_version_line:
        print(f"No changes needed for {filepath} (already at {new_version_line}).")
        return True

    if dry_run:
        print(f"[DRY RUN] Would update {filepath}:")
        print(f"  - {old_version_line}")
        print(f"  + {new_version_line}")
    else:
        new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        with open(filepath, "w") as f:
            f.write(new_content)
        print(f"Updated {filepath}: {old_version_line} -> {new_version_line}")

    return True


def main():
    parser = argparse.ArgumentParser(description="Bump version across project files.")
    parser.add_argument("new_version", help="The new version string (e.g., 1.2.3)")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without modifying files",
    )
    args = parser.parse_args()

    new_version = args.new_version
    dry_run = args.dry_run

    if dry_run:
        print(f"--- PREVIEWING BUMP TO {new_version} ---")

    # 1. Update pyproject.toml
    # Use a regex that specifically targets the version field,
    # ensuring it's at the start of a line to avoid matching
    # target-version or python_version.
    update_file(
        "pyproject.toml",
        r'^version\s*=\s*"[^"]+"',
        f'version = "{new_version}"',
        dry_run=dry_run,
    )

    # 2. Update manifest.json
    manifest_path = "custom_components/catholic_calendar/manifest.json"
    try:
        if os.path.exists(manifest_path):
            with open(manifest_path) as f:
                manifest = json.load(f)

            old_version = manifest.get("version", "unknown")
            if old_version != new_version:
                if dry_run:
                    print(f"[DRY RUN] Would update {manifest_path}:")
                    print(f'  - "version": "{old_version}"')
                    print(f'  + "version": "{new_version}"')
                else:
                    manifest["version"] = new_version
                    with open(manifest_path, "w") as f:
                        json.dump(manifest, f, indent=2)
                        f.write("\n")
                    print(
                        f"Updated {manifest_path}: "
                        f'"version": "{old_version}" -> "{new_version}"'
                    )

            else:
                print(f"No changes needed for {manifest_path} (already {new_version}).")
        else:
            print(f"File not found: {manifest_path}")
    except Exception as e:
        print(f"Failed to update manifest.json: {e}")

    # 3. Update sensor.py
    update_file(
        "custom_components/catholic_calendar/sensor.py",
        r'__version__\s*=\s*"[^"]+"',
        f'__version__ = "{new_version}"',
        dry_run=dry_run,
    )

    # 4. Update calendar.py
    update_file(
        "custom_components/catholic_calendar/calendar.py",
        r'__version__\s*=\s*"[^"]+"',
        f'__version__ = "{new_version}"',
        dry_run=dry_run,
    )

    if dry_run:
        print(f"\nDry run complete for version {new_version}.")
    else:
        print(f"\nSuccessfully bumped version to {new_version} across all files.")


if __name__ == "__main__":
    main()
