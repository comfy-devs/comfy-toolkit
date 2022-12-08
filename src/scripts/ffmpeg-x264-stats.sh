#!/bin/bash
# Stats (TXT)
# Arguments: 1 (source .mp4 file), 2 (destination folder), 3 (episode ID)

V_BITRATE=$(ffprobe -i "$1" -v quiet -select_streams v:0 -show_entries stream=bit_rate -hide_banner -of default=noprint_wrappers=1:nokey=1)
A_BITRATE=$(ffprobe -i "$1" -v quiet -select_streams a:0 -show_entries stream=bit_rate -hide_banner -of default=noprint_wrappers=1:nokey=1)
SIZE=$(stat --format "%s" "$1")
DURATION=$(ffprobe -i "$1" -v quiet -show_entries format=duration -hide_banner -of default=noprint_wrappers=1:nokey=1)
RESULT="INSERT IGNORE INTO encodes (id, episode, preset, videoBitrate, audioBitrate, size) VALUES (\"$3-0\", \"$3\", 0, $V_BITRATE, $A_BITRATE, $SIZE)"
RESULT="$RESULT\nUPDATE episodes SET duration=$DURATION WHERE id=\"$3\""
echo $RESULT > $2/stats_x264.sql