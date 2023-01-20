#!/bin/bash
# Video (x264 - 1080p) + Audio (AAC)
# All quality preserving options enabled, slow preset
# Arguments: 1 (source .mkv file), 2 (destination folder), 3 (tune), 4 (fps), 5 (audio mappings)

ffmpeg -i "$1" -loglevel error -stats -pix_fmt yuv420p -c:v libx264 -c:a libfdk_aac -map 0:v:0 $5 -map -0:s -map -0:d -map -0:t -b:a 192k -vbr 5 -movflags +faststart -preset slow -tune $3 -x264-params "b-adapt=2:bframes=8:aq-mode=3:aq-strength=0.7:direct=auto:trellis=2:rc-lookahead=128:crf=20:me=umh:subme=10:min-keyint=$4" "$2/episode_x264.mp4" 
