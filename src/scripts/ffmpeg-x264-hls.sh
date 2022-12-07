#!/bin/bash
# Splits x264 video onto 3 HLS streams
# First one is original, second is 720p with 96k audio, third is 480p with 72k audio
# Arguments: 1 (source .mp4 file), 2 (destination folder)

ffmpeg -i "$1" -filter_complex "[0:v]split=3[v1][v2][v3]; [v1]copy[v1m]; [v2]scale=w=1280:h=720[v2m]; [v3]scale=w=854:h=480[v3m]" -map [v1m] -map [v2m] -map [v3m] -map a:0 -c:a:0 libfdk_aac -map a:0 -c:a:1 libfdk_aac -b:a:1 96k -map a:0 -c:a:2 libfdk_aac -b:a:2 72k -f hls -hls_playlist_type vod -hls_flags single_file+independent_segments -hls_segment_type mpegts -hls_segment_filename "$2/hls/x264/%v/stream.ts" -master_pl_name "master.m3u8" -var_stream_map "v:0,a:0 v:1,a:1 v:2,a:2" -muxdelay 0 "$2/hls/x264/%v/playlist.m3u8"
