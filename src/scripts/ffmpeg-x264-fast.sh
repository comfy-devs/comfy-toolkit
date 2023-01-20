#!/bin/bash
# Video (x264 - 1080p) + Audio (AAC - 192k)
# No quality preserving options enabled, medium preset
# Arguments: 1 (source .mkv file), 2 (destination folder), 3 (tune), 4 (audio mappings)

ffmpeg -i "$1" -loglevel error -stats -pix_fmt yuv420p -c:v libx264 -c:a libfdk_aac -map 0:v:0 $4 -map -0:s -map -0:d -map -0:t -b:a 192k -vbr 5 -movflags +faststart -preset medium -tune $3 "$2/episode_x264.mp4" 
