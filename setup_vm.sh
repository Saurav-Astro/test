#!/bin/bash

# ProXM Azure VM Setup Script
echo "Starting ProXM Setup..."

# 1. Update and install basic tools
sudo apt-get update
sudo apt-get install -y git curl apt-transport-https ca-certificates software-properties-common

# 2. Install Docker
if ! command -v docker &> /dev/null
then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
else
    echo "Docker already installed."
fi

# 3. Install Docker Compose
if ! command -v docker-compose &> /dev/null
then
    echo "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
else
    echo "Docker Compose already installed."
fi

# 4. Handle Proxy (Optional - uncomment if needed)
# export http_proxy="http://your-proxy:port"
# export https_proxy="http://your-proxy:port"
# git config --global http.proxy http://your-proxy:port

echo "Setup complete. To start the project, run:"
echo "docker-compose up --build -d"
