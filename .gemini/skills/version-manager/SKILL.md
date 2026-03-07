---
name: version-manager
description: Automatically calculate and update semantic version numbers based on code changes for the Catholic Calendar integration. Use this when the user wants to update the version strings in pyproject.toml, manifest.json, sensor.py, and calendar.py.
---

# Version Manager

This skill provides a streamlined, "read-only" (with respect to Git) workflow for updating version strings across the integration.

## Workflow

When asked to update the version based on changes:

### 1. Analyze Changes
1. Inspect the current unstaged or staged changes using `git diff HEAD`.
2. Apply Semantic Versioning (SemVer) principles to decide the bump type:
   - **MAJOR**: Breaking changes (e.g., removing YAML support, changing Domain).
   - **MINOR**: New features or significant refactoring (e.g., adding Vespers-aware logic).
   - **PATCH**: Bug fixes or minor internal cleanup.

### 2. Determine Current Version
Read `custom_components/catholic_calendar/manifest.json` to find the current version string.

### 3. Execute the Version Bump
Use the bundled Python script to update all files. Replace `<new_version>` with your calculated version (e.g., `2.1.0`):

```bash
python3 .gemini/skills/version-manager/scripts/bump_version.py <new_version>
```

### 4. Final Review
Confirm to the user which files were updated and what the new version is. Do NOT stage or commit the changes.
