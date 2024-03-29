#!/bin/bash
# Video (VP9 - 1080p) + Audio (Opus - 192k)
# Arguments: 1 (source .mkv file), 2 (destination folder), 3 (minimal bitrate), 4 (bitrate), 5 (maximal bitrate), 6 (audio mappings)

OPTS="-loglevel error -stats -pix_fmt yuv420p -c:v libvpx-vp9 -profile:v 0 -map 0:v:0 -map -0:s -map -0:d -map -0:t -metadata:s:v bit_rate=$4 -metadata:s:a bit_rate=192k -crf 28 -b:v $4 -minrate $3 -maxrate $5 -threads 12 -deadline good -cpu-used 3 -frame-parallel 1 -tile-columns 2 -tile-rows 2 -row-mt 1 -lag-in-frames 25 -auto-alt-ref 1 -arnr-maxframes 7 -arnr-strength 5 -aq-mode 0 -tune-content default -enable-tpl 1"

ffmpeg -i "$1" $OPTS -pass 1 -an -f null /dev/null && \
ffmpeg -i "$1" $OPTS -pass 2 -c:a libopus $6 -b:a 192k -vbr 1 -mapping_family 1 -ac 2 "$2/episode_vp9.webm"
