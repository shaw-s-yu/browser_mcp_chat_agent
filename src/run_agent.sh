#!/bin/bash

# This script is designed to be run inside the Docker container.
# It activates the virtual environment and then runs the browser agent.

# Activate the virtual environment
source ~/app/venv/bin/activate

# Run the chat agent script
python3 ~/app/chat_agent.py
