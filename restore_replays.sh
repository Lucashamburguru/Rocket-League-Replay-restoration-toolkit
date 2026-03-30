#!/bin/bash

# --- Rocket League Replay Restorer (v1.0) ---
# For Linux / Steam Deck users

# Ensure we're in the script's directory
cd "$(dirname "$0")"

# Check for Python 3
if ! command -v python3 &> /dev/null
then
    echo "Error: Python 3 is not installed. Please install it to continue."
    exit 1
fi

# Create default directories if they don't exist
mkdir -p ./input_replays
mkdir -p ./restored_replays

# Check if there are replays to process
REPLAY_COUNT=$(ls -1 ./input_replays/*.replay 2>/dev/null | wc -l)

if [ "$REPLAY_COUNT" -eq 0 ]; then
    echo "--- No Replays Found ---"
    echo "1. Place your legacy .replay files into the 'input_replays' folder."
    echo "2. Run this script again."
    exit 0
fi

# Run the restorer
python3 universal_batch_converter.py --input ./input_replays --output ./restored_replays

echo ""
echo "Don't forget to copy the files from 'restored_replays' to your Rocket League Demos folder!"
read -p "Press Enter to close..."
