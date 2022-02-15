#!/bin/bash
# Splits VP9 video onto 3 HLS streams (with 2 audio streams for dubbed)
# First one is original, second is 720p with 96k audio, third is 480p with 72k audio
# Arguments: 1 (source .webm file), 2 (destination folder)

ffmpeg -i "$1" -filter_complex "[0:v]split=3[v1][v2][v3]; [v1]copy[v1m]; [v2]scale=w=1280:h=720[v2m]; [v3]scale=w=854:h=480[v3m]" -map [v1m] -map [v2m] -map [v3m] -map a:0 -c:a:0 libopus -map a:0 -c:a:1 libopus -b:a:1 96k -map a:0 -c:a:2 libopus -b:a:2 72k -map a:1 -c:a:3 libfdk_aac -map a:1 -c:a:4 libfdk_aac -b:a:4 96k -map a:1 -c:a:5 libfdk_aac -b:a:5 72k -f hls -hls_playlist_type vod -hls_flags single_file+independent_segments -hls_segment_type mpegts -hls_segment_filename "$2/hls/vp9/%v/stream.ts" -master_pl_name "master.m3u8" -var_stream_map "v:0,a:0,a:3 v:1,a:1,a:4 v:2,a:2,a:5" "$2/hls/vp9/%v/playlist.m3u8"