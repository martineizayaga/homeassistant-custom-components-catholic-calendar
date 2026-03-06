#!/bin/bash

# 1. Set up Home Assistant Core repository
if [ ! -d "ha_core" ]; then
    git clone --depth 1 https://github.com/home-assistant/core.git ha_core
else
    cd ha_core && git pull && cd ..
fi

# 2. Link your custom component
mkdir -p ha_core/custom_components
if [ ! -L "ha_core/custom_components/catholic_calendar" ]; then
    ln -s ../../custom_components/catholic_calendar ha_core/custom_components/catholic_calendar
fi

# 3. Create venv and install dependencies via uv
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

# Only rebuild venv if it's missing or if forced
if [ ! -d "venv" ]; then
    uv venv venv
fi

source venv/bin/activate

# Upgrade project dependencies
cd ha_core
uv pip install --upgrade -r requirements.txt
uv pip install --upgrade -e .
uv pip install --upgrade ruff mypy
cd ..

# 4. Set up configuration.yaml with catholic_calendar integration
CONFIG_DIR="ha_core/config"
CONFIG_FILE="$CONFIG_DIR/configuration.yaml"

mkdir -p "$CONFIG_DIR"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "Creating new configuration.yaml..."
    cat <<EOF > "$CONFIG_FILE"
# Manual set of integrations to avoid go2rtc/default_config failures
frontend:
  themes: !include_dir_merge_named themes

# Essential components for the UI and operation
config:
my:
history:
logbook:
system_health:

automation: !include automations.yaml
script: !include scripts.yaml
scene: !include scenes.yaml

logger:
  default: info
  logs:
    custom_components.catholic_calendar: debug

sensor:
  - platform: catholic_calendar
    name: "Catholic Sensor"

calendar:
  - platform: catholic_calendar
    name: "Catholic Calendar"
EOF
    # Create referenced files to avoid errors
    touch "$CONFIG_DIR/automations.yaml" "$CONFIG_DIR/scripts.yaml" "$CONFIG_DIR/scenes.yaml"
elif ! grep -q "catholic_calendar" "$CONFIG_FILE"; then
    echo "Adding catholic_calendar to existing configuration.yaml..."
    cat <<EOF >> "$CONFIG_FILE"

# Catholic Calendar Integration added by devcontainer
logger:
  logs:
    custom_components.catholic_calendar: debug

sensor:
  - platform: catholic_calendar
    name: "Catholic Sensor"

calendar:
  - platform: catholic_calendar
    name: "Catholic Calendar"
EOF
fi

# 5. Optionally install gemini-cli
if [ "$SKIP_GEMINI_CLI" != "true" ]; then
    echo "Installing gemini-cli..."
    brew install gemini-cli
else
    echo "Skipping gemini-cli installation as SKIP_GEMINI_CLI is set to true."
fi
