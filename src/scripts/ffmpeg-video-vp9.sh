# /bin/bash
# Video (VP9 - 1080p) + Audio (Opus)

OPTS="-loglevel error -stats -pix_fmt yuv420p -vcodec libvpx-vp9 -map 0:v:0 -map -0:s -map -0:d -map -0:t -profile:v 0 -crf 15 -b:v $4 -minrate $3 -maxrate $5 -threads 12 -frame-parallel 1 -tile-columns 2 -tile-rows 2 -row-mt 1 -lag-in-frames 25 -arnr-maxframes 7 -arnr-strength 5 -aq-mode 0 -tune-content default -enable-tpl 1"

ffmpeg -i "$1" $OPTS -pass 1 -an -f null /dev/null && \
ffmpeg -i "$1" $OPTS -pass 2 -acodec libopus -map 0:a:0 -vbr 1 "$2/ep_vp.webm"
