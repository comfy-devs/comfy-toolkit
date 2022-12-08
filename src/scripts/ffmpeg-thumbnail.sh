#!/bin/bash
# Thumbnail (WEBP)
# Arguments: 1 (source .mp4 file), 2 (destination folder)

ffmpeg -ss "$(bc -l <<< "$(ffprobe -loglevel error -of csv=p=0 -show_entries format=duration "$1")*0.5")" -i "$1" -loglevel error -stats -vframes 1 "$2/thumbnail.jpg"
ffmpeg -ss "$(bc -l <<< "$(ffprobe -loglevel error -of csv=p=0 -show_entries format=duration "$1")*0.5")" -i "$1" -loglevel error -stats -vframes 1 "$2/thumbnail.webp"
