#!/bin/bash
# Stats (TXT)
# Arguments: 1 (source .mp4 file), 2 (destination folder)

VIDEO_BITRATE=$(ffprobe -i "$1" -v quiet -select_streams v:0 -show_entries stream=bit_rate -hide_banner -of default=noprint_wrappers=1:nokey=1)
AUDIO_BITRATE=$(ffprobe -i "$1" -v quiet -select_streams a:0 -show_entries stream=bit_rate -hide_banner -of default=noprint_wrappers=1:nokey=1)
SIZE=$(stat --format "%s" "$1")
DURATION=$(ffprobe -i "$1" -v quiet -show_entries format=duration -hide_banner -of default=noprint_wrappers=1:nokey=1)

cat > $2/stats.json<< EOF
{
    "videoBitrate": $VIDEO_BITRATE,
    "audioBitrate": $AUDIO_BITRATE,
    "size": $SIZE,
    "duration": $DURATION
}
EOF