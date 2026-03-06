#!/bin/bash
# postStartCommand.sh runs every time the container starts.

echo "Checking for system and project updates..."

# 1. Update System Packages (Apt & Brew)
# We use sudo because the container runs as the 'vscode' user.
echo "Updating apt package list..."
sudo apt-get update && sudo apt-get upgrade -y

echo "Updating Homebrew packages..."
brew update && brew upgrade

# 2. Update Home Assistant Core (fast git pull)
if [ -d "ha_core" ]; then
    echo "Updating ha_core..."
    cd ha_core && git pull && cd ..
fi

# 3. Update Python dependencies (uv is fast and skips if already current)
if [ -d "venv" ]; then
    echo "Updating python dependencies..."
    source venv/bin/activate
    cd ha_core
    uv pip install --upgrade -r requirements.txt
    uv pip install --upgrade -e .
    cd ..
fi

echo "Dev Container is ready and fully updated!"
