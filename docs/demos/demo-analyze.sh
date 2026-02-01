#!/bin/bash
# Demo script for mixref analyze command

cd /workspace/mixref

# Clear screen
clear

# Show command
echo "$ mixref analyze data/example.wav --genre dnb"
echo ""
sleep 1

# Run the command
uv run mixref analyze data/example.wav --genre dnb

sleep 3
