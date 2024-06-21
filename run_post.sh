#!/bin/bash

# This is a shell script to run post.py
# Navigate to the project directory
cd /path/to/project

# Source the environment variables from your shell (example: zsh)
source /path/to/.zshrc

# Run the Python script using Poetry
/path/to/.local/bin/poetry run python post.py >> /path/to/project/cron.log 2>&1

