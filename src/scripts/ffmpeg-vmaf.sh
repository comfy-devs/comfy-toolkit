#!/bin/bash
# VMAF score (TXT)
# Arguments: 1 (source .mkv file), 2 (encoded .mp4/.webm file)

ffmpeg -i "$1" -i "$2" -lavfi libvmaf=n_threads=12 -f null -