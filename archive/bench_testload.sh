#! /usr/bin/env bash

# Get the list of models
MODELS=($(ollama list | awk '{print $1}' | tail -n +2 ))

# Loop through each of the selected models
for ITEM in "${MODELS[@]}"; do
    echo "--------------------------------------------------------------"
    echo "Loading model $ITEM"
    ollama run "$ITEM" ""
    ollama run "$ITEM" ""
    ollama run "$ITEM" ""
    ollama run "$ITEM" ""
    ollama run "$ITEM" ""
    echo "--------------------------------------------------------------"
done