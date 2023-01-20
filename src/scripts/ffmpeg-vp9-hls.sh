#!/bin/bash
# Splits VP9 video onto 3 FMP4 HLS video streams (VP9)
# First one is original, second is 720p, third is 480p (no audio is included)
# Arguments: 1 (source .webm file), 2 (destination folder)

ffmpeg -i "$1" -filter_complex "[0:v]split=3[v1][v2][v3]; [v1]copy[v1m]; [v2]scale=w=1280:h=720[v2m]; [v3]scale=w=854:h=480[v3m]" -map [v1m] -map [v2m] -map [v3m] -f hls -hls_playlist_type vod -hls_flags single_file+independent_segments -hls_segment_type fmp4 -hls_segment_filename "$2/hls/vp9/%v/stream.mp4" -master_pl_name "master.m3u8" -var_stream_map "v:0 v:1 v:2" -muxdelay 0 "$2/hls/vp9/%v/playlist.m3u8"
