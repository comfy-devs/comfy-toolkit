#!/bin/bash
# Video (x264 - 1080p) + Audio (AAC)
# Almost no quality improving options enabled, medium preset
# Arguments: 1 (source .mkv file), 2 (destination folder)

ffmpeg -i "$1" -loglevel error -stats -pix_fmt yuv420p -vcodec libx264 -acodec libfdk_aac -map 0:v:0 -map 0:a -map -0:s -map -0:d -map -0:t -vbr 5 -movflags +faststart -preset medium -tune animation "$2/episode_x264.mp4" 
