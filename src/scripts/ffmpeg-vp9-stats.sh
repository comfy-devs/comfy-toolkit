#!/bin/bash
# Stats (TXT)
# Arguments: 1 (source .webm file), 2 (destination folder), 3 (episode ID)

V_BITRATE=$(ffprobe -i "$1" -v quiet -select_streams v:0 -show_entries stream -hide_banner -of default=noprint_wrappers=1 | grep TAG:NUMBER_OF_BYTES | sed "s/TAG:NUMBER_OF_BYTES-eng=//")
A_BITRATE=$(ffprobe -i "$1" -v quiet -select_streams a:0 -show_entries stream -hide_banner -of default=noprint_wrappers=1 | grep TAG:NUMBER_OF_BYTES | sed "s/TAG:NUMBER_OF_BYTES-eng=//")
SIZE=$(stat --format "%s" "$1")
DURATION=$(ffprobe -i "$1" -v quiet -show_entries format=duration -hide_banner -of default=noprint_wrappers=1:nokey=1)
let "V_BITRATE = $V_BITRATE / $DURATION"
let "A_BITRATE = $A_BITRATE / $DURATION"
RESULT="INSERT IGNORE INTO encodes (id, episode, preset, videoBitrate, audioBitrate, size, duration) VALUES (\"$3-1\", \"$3\", 1, $V_BITRATE, $A_BITRATE, $SIZE, $DURATION)"
echo $RESULT > $2/stats_vp9.sql