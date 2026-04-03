#!/bin/bash
# Rocket League Replay Restorer (v1.4) - Linux Version

# Colors
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${CYAN}-------------------------------------------------------------------${NC}"
echo -e "    Rocket League Replay Restorer (v1.4) - Restoration Toolkit"
echo -e "${CYAN}-------------------------------------------------------------------${NC}"
echo ""
echo "     _ "
echo "    ( )"
echo "   (o o)"
echo "   ( v )"
echo "  /|   |\\"
echo "   ^   ^"
echo "Made by Pengo & Gemini"
echo ""

# Check for python3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed.${NC}"
    exit 1
fi

# Create default directories
mkdir -p input_replays
mkdir -p restored_replays

# Check for replays
if [ -z "$(ls -A input_replays/*.replay 2>/dev/null)" ]; then
    echo "--- No Replays Found ---"
    echo ""
    echo "1. Put your legacy .replay files into the 'input_replays' folder."
    echo "2. Run this script again."
    echo ""
    exit 0
fi

# Run the latest stable restorer
echo "Processing replays..."
python3 universal_batch_converter.py --input ./input_replays --output ./restored_replays

echo ""
echo "Operation complete."
echo "Restored files available in: ./restored_replays"
echo ""
