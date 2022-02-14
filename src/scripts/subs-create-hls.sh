#!/bin/bash
# Creates an HLS subtitle playlist
# Arguments: 1 (source .vtt relative path), 2 (duration), 3 (destination file name)

cat > $3<< EOF
#EXTM3U
#EXT-X-VERSION:6
#EXT-X-TARGETDURATION:10
#EXT-X-MEDIA-SEQUENCE:0
#EXT-X-PLAYLIST-TYPE:VOD
#EXTINF:$2,
$1
#EXT-X-ENDLIST
EOF