#!/bin/bash
# Video (x264 - 1080p) + Audio (AAC)

ffmpeg -i "$1" -loglevel error -stats -pix_fmt yuv420p -vcodec libx264 -acodec libfdk_aac -map 0:v:0 -map 0:a:0 -map -0:s -map -0:d -map -0:t -vbr 5 -movflags +faststart -preset slow -tune animation -x264-params "b-adapt=2:bframes=8:aq-mode=3:aq-strength=0.7:direct=auto:trellis=2:rc-lookahead=128:crf=20:me=umh:subme=10:min-keyint=24" "$2/ep_high.mp4" 
