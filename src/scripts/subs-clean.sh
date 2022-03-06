#!/bin/bash
# Basic cleaning of VTT subtitles
# Arguments: 1 (source .vtt file)

perl -pe "s|\{(.+?(?=\}))\}||gm" "$1" > "$1.txt" 
mv -f "$1.txt" "$1"
