# /bin/bash
# Thumbnail (WEBP)

ffmpeg -ss "$(bc -l <<< "$(ffprobe -loglevel error -of csv=p=0 -show_entries format=duration "$1")*0.5")" -i "$1" -loglevel error -stats -vframes 1 "$2/thumbnail.webp"
