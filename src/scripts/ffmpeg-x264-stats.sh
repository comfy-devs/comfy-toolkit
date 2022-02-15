#!/bin/bash
# Stats (TXT)
# Arguments: 1 (source .mp4 file), 2 (destination folder)

RESULT="${RESULT}INSERT INTO encodes (id, episode, preset, videoBitrate, audioBitrate, size, duration) VALUES (\"$entry-$item-4\", \"$entry-$item\", 4, $(ffprobe -i "/mnt/raid/nyananime-xyz-video/$entry/$item/ep_high.mp4" -v quiet -select_streams v:0 -show_entries stream=bit_rate -hide_banner -of default=noprint_wrappers=1:nokey=1), $(ffprobe -i "/mnt/raid/nyananime-xyz-video/$entry/$item/ep_high.mp4" -v quiet -select_streams a:0 -show_entries stream=bit_rate -hide_banner -of default=noprint_wrappers=1:nokey=1), $(stat --format "%s" "/mnt/raid/nyananime-xyz-video/$entry/$item/ep_high.mp4"), $(ffprobe -i "/mnt/raid/nyananime-xyz-video/$entry/$item/ep_high.mp4" -v quiet -show_entries format=duration -hide_banner -of default=noprint_wrappers=1:nokey=1))\n"