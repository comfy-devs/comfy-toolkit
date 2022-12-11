#!/bin/bash
# Subtitles (VTT)
# Arguments: 1 (source .mkv file), 2 (destination .vtt file), 3 (index)

ffmpeg -i "$1" -loglevel error -stats -map 0:s:$3 "$2"
