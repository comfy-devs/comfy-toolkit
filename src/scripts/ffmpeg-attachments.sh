#!/bin/bash
# Attachments (fonts, etc)
# Arguments: 1 (source .mkv file), 2 (destination folder)

cd "$2/attachments"
ffmpeg -dump_attachment:t "" -i "$1" -loglevel error -stats
