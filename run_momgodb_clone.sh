#!/bin/bash

# Configuration
ENV_NAME="mongo_cloner_env"
PYTHON_VERSION="3.10"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REQUIREMENTS="$SCRIPT_DIR/requirements.txt"
MAIN_SCRIPT="$SCRIPT_DIR/main_mongo.py"

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo "Error: conda not found. Please install Miniconda or Anaconda."
    exit 1
fi

# Search for existing environment
ENV_EXISTS=$(conda env list | grep "$ENV_NAME")

if [ -z "$ENV_EXISTS" ]; then
    echo "Creating conda environment: $ENV_NAME..."
    conda create -y -n "$ENV_NAME" python="$PYTHON_VERSION"
else
    echo "Conda environment $ENV_NAME already exists."
fi

# Activate environment and install dependencies
echo "Activating environment and installing dependencies..."
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$ENV_NAME"

if [ -f "$REQUIREMENTS" ]; then
    pip install -r "$REQUIREMENTS"
else
    echo "Warning: requirements.txt not found at $REQUIREMENTS"
fi

# Run the script
if [ -f "$MAIN_SCRIPT" ]; then
    echo "Launching MongoDB Cloner..."
    python "$MAIN_SCRIPT"
else
    echo "Error: main_mongo.py not found at $MAIN_SCRIPT"
    exit 1
fi
