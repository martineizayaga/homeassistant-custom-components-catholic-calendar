FROM mcr.microsoft.com/devcontainers/base:noble

# 1. Install STABLE APT dependencies (Cached long-term)
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    python3-pip python3-dev python3-venv autoconf libssl-dev libxml2-dev \
    libxslt1-dev libjpeg-dev libffi-dev libudev-dev zlib1g-dev pkg-config \
    libavformat-dev libavcodec-dev libavdevice-dev libavutil-dev libswscale-dev \
    libswresample-dev libavfilter-dev ffmpeg libgammu-dev build-essential \
    gcc-12 g++-12 sudo

# 2. Switch to vscode user for Homebrew and Gemini
USER vscode
ENV NONINTERACTIVE=1
RUN /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 3. Add brew to PATH
ENV PATH="/home/linuxbrew/.linuxbrew/bin:${PATH}"

# Stay as vscode user so scripts run with correct permissions
USER vscode