#!/bin/bash
# Chapters (TXT)
# Arguments: 1 (source .mp4 file), 2 (destination folder)

ffprobe -show_chapters -print_format json -loglevel error "$1" > "$2/chapters.json"
