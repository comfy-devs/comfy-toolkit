#!/bin/bash
# Video (x264 - 1080p) + Audio (AAC)

ffmpeg -i "$1" -loglevel error -stats -pix_fmt yuv420p -vcodec libx264 -map 0:v:0 -map 0:a:0 -map -0:s -map -0:d -map -0:t -vbr 5 -movflags +faststart -preset medium -tune animation "$2/ep_high.mp4" 
