#!/bin/bash
# Timeline (WEBP)
# Arguments: 1 (source .mkv file), 2 (destination folder), 3 (start time), 4 (start second), 5 (interval)

ffmpeg -ss $3 -i "$1" -frames 1 -vf "select=not(mod(n\,$5)),scale=320:180,tile=6x6" -loglevel error -stats "$2/timeline_$4.webp"
