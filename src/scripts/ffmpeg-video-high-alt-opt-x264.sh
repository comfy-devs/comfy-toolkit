# /bin/bash
# Video (x264 - 1080p) + Audio (AAC)
# Modified options (rc-lookahead, b-adapt, trellis, me, subme)

ffmpeg -i "$1" -loglevel error -stats -pix_fmt yuv420p -vcodec libx264 -acodec libfdk_aac -map 0:v:0 -map 0:a:0 -map -0:s -map -0:d -map -0:t -vbr 5 -movflags +faststart -preset medium -tune animation -x264-params "bframes=8:aq-mode=3:aq-strength=0.7:direct=auto:rc-lookahead=72:crf=20:min-keyint=24" "$2/ep_high.mp4" 
