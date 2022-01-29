#!/bin/bash
# Chapters (TXT)

ffprobe -show_chapters -print_format json -loglevel error "$1" > "$2/chapters.json"
