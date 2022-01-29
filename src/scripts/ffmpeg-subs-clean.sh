#!/bin/bash
# Basic cleaning of VTT subtitles

perl -pe "s|\{(.+?(?=\}))\}|a|gm" "$1/subs_en.vtt" > "$1/subs_en_out.vtt" 
mv -f "$1/subs_en_out.vtt" "$1/subs_en.vtt"
