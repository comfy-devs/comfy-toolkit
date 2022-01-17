# /bin/bash
# Subtitles (VTT)

ffmpeg -i "$1" -loglevel error -stats -map 0:s:0 "$2/subs_en.vtt"
