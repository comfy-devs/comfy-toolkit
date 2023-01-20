#!/bin/bash
# Splits original video onto 3 HLS audio streams (Opus)
# First one is 192k, second is 152k, third is 128k (as per Youtube's audio chart)
# Arguments: 1 (source .mkv file), 2 (destination folder), 3 (index), 4 (language)

ffmpeg -i "$1" -loglevel error -stats -c:a:0 libopus -map a:$3 -b:a:0 192k -c:a:1 libopus -map a:$3 -b:a:1 152k -c:a:2 libopus -map a:$3 -b:a:2 128k -ac 2 -f hls -hls_playlist_type vod -hls_flags single_file+independent_segments -hls_segment_type fmp4 -hls_segment_filename "$2/hls/audio/%v/$4.mp4" -var_stream_map "a:0 a:1 a:2" -muxdelay 0 "$2/hls/audio/%v/$4.m3u8"
