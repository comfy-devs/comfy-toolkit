#!/bin/bash
# Stats (TXT)
# Arguments: 1 (source .webm file), 2 (destination folder)

# TODO: calculate bitrate
VIDEO_BITRATE=$(ffprobe -i "$1" -v quiet -select_streams v:0 -show_entries stream -hide_banner -of default=noprint_wrappers=1 | grep TAG:NUMBER_OF_BYTES | sed "s/TAG:NUMBER_OF_BYTES-eng=//")
AUDIO_BITRATE=$(ffprobe -i "$1" -v quiet -select_streams a:0 -show_entries stream -hide_banner -of default=noprint_wrappers=1 | grep TAG:NUMBER_OF_BYTES | sed "s/TAG:NUMBER_OF_BYTES-eng=//")
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