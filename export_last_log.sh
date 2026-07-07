#!/bin/bash

LOG_FILE="$HOME/iptv.log"

OUTPUT="/sdcard/Download/iptv_last_result.txt"

echo "===== IPTV LAST LOG =====" > "$OUTPUT"
date >> "$OUTPUT"
echo "" >> "$OUTPUT"

tail -200 "$LOG_FILE" >> "$OUTPUT"

echo "Saved to: $OUTPUT"
