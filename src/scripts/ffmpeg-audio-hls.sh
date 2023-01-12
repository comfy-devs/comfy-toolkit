#!/bin/bash
# Splits x264 video onto 3 HLS audio streams
# First one is original, second is 152k, third is 128k (as per Youtube's audio chart)
# Arguments: 1 (source .mp4 file), 2 (destination folder), 3 (index), 4 (language)

ffmpeg -i "$1" -loglevel error -stats -map a:$3 -c:a:0 libfdk_aac -map a:$3 -c:a:1 libfdk_aac -b:a:1 152k -map a:$3 -c:a:2 libfdk_aac -b:a:2 128k -f hls -hls_playlist_type vod -hls_flags single_file+independent_segments -hls_segment_type mpegts -hls_segment_filename "$2/hls/audio/%v/$4.ts" -var_stream_map "a:0 a:1 a:2" -muxdelay 0 "$2/hls/audio/%v/$4.m3u8"
