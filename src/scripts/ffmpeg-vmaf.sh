#!/bin/bash
# VMAF score (TXT)
# Arguments: 1 (source .mkv file), 2 (encoded .mp4/.webm file), 3 (log path)

ffmpeg -i "$1" -i "$2" -stats -lavfi "[0:v]crop=480:360,setpts=PTS-STARTPTS[reference];[1:v]crop=480:360,setpts=PTS-STARTPTS[distorted];[distorted][reference]libvmaf=n_threads=12:n_subsample=2" -f null -