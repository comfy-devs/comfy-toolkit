#!/bin/bash
# Stats (TXT)
# Arguments: 1 (source .mp4/.webm file), 2 (destination .sql file), 3 (episode ID), 4 (preset), 5 (fps)

V_BITRATE=$(ffprobe -i "$1" -v quiet -select_streams v:0 -show_entries stream=bit_rate -hide_banner -of default=noprint_wrappers=1:nokey=1)
A_BITRATE=$(ffprobe -i "$1" -v quiet -select_streams a:0 -show_entries stream=bit_rate -hide_banner -of default=noprint_wrappers=1:nokey=1)
SIZE=$(stat --format "%s" "$1")
DURATION=$(ffprobe -i "$1" -v quiet -show_entries format=duration -hide_banner -of default=noprint_wrappers=1:nokey=1)

cat > $2<< EOF
INSERT IGNORE INTO encodes (id, episode, preset, videoBitrate, audioBitrate, size) VALUES ("$3-$4", "$3", $4, $V_BITRATE, $A_BITRATE, $SIZE);
UPDATE episodes SET duration=$DURATION, fps=$5 WHERE id="$3";
EOF