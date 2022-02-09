#!/bin/bash
# Additional cleaning of VTT subtitles
# Arguments: 1 (source folder)

cd ../clean-vtt
yarn process "$1" "$1.txt"
mv -f "$1.txt" "$1"
cd ../scripts
