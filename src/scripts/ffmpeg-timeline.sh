#!/bin/bash
# Timeline (WEBP)
# Arguments: 1 (source .mp4 file), 2 (destination folder), 3 (start time), 4 (start second)

ffmpeg -ss $3 -i "$1" -frames 1 -vf "select=not(mod(n\,120)),scale=320:180,tile=6x6" -loglevel error -stats "$2/timeline_$4.webp"