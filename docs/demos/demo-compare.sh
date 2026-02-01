#!/bin/bash
# Demo script for mixref compare command

cd /workspace/mixref

# Clear screen
clear

# Show command
echo "$ mixref compare data/example.wav data/example.mp3 --bpm --key"
echo ""
sleep 1

# Run the command
uv run mixref compare data/example.wav data/example.mp3 --bpm --key

sleep 3
