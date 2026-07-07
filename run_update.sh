#!/bin/bash

cd /root/projects

. /root/projects/myenv/bin/activate

DATE=$(date +"%Y-%m-%d_%H-%M-%S")

LOGFILE="/sdcard/Download/IPTV_Run_$DATE.txt"

echo "===================================" > "$LOGFILE"
echo "IPTV Update Run" >> "$LOGFILE"
echo "Date: $(date)" >> "$LOGFILE"
echo "===================================" >> "$LOGFILE"
echo "" >> "$LOGFILE"

/usr/bin/xvfb-run -a python /root/projects/update_iptv.py >> "$LOGFILE" 2>&1

echo "" >> "$LOGFILE"
echo "===================================" >> "$LOGFILE"
echo "Finished: $(date)" >> "$LOGFILE"
echo "===================================" >> "$LOGFILE"
