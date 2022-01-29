#!/bin/bash
# Checks compability/data about an episode folder

V_FILE=$(find "$1" -type f -exec file -N -i -- {} + | sed -n 's!: video/[^:]*$!!p')
S_FILES=$(find "$1" -name subs_en.vtt | wc -l)
T_FILES=$(find "$1" -name thumbnail.webp | wc -l)
C_FILES=$(find "$1" -name chapters.json | wc -l)
ST_FILES=$(find "$1" -name stats.json | wc -l)

FORMAT=$(ffprobe -v error -show_entries format=format_name -of default=noprint_wrappers=1:nokey=1 "$V_FILE")
V_AMMOUNT=$(ffprobe -v error -select_streams V -show_entries stream=index -of csv=p=0 "$V_FILE" | wc -w)
V_CODEC=$(ffprobe -v error -select_streams v:0 -show_entries stream=codec_name -of csv=p=0 "$V_FILE")
A_AMMOUNT=$(ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "$V_FILE" | wc -w)
S_AMMOUNT=$(ffprobe -v error -select_streams s -show_entries stream=index -of csv=p=0 "$V_FILE" | wc -w)
D_AMMOUNT=$(ffprobe -v error -select_streams d -show_entries stream=index -of csv=p=0 "$V_FILE" | wc -w)
T_AMMOUNT=$(ffprobe -v error -select_streams t -show_entries stream=index -of csv=p=0 "$V_FILE" | wc -w)
A_CODEC=$(ffprobe -v error -select_streams a:0 -show_entries stream=codec_name -of csv=p=0 "$V_FILE")
V_PIXFMT=$(ffprobe -v error -select_streams v:0 -show_entries stream=pix_fmt -of csv=p=0 "$V_FILE")
IS_FAST_START=$(ffprobe -v debug "$V_FILE" 2>&1 | grep seeks:0)

GRAY="\033[0;37m"
BLUE="\033[0;34m"
RED="\033[0;31m"
GREEN="\033[0;32m"
RESET="\033[0m"

echo -e  "┃ Folder: $GRAY'$1'$RESET"
echo -e  "┗━┓$BLUE Video$RESET"
echo -e  "  ┣━ Filename: $GRAY$V_FILE$RESET"
echo -ne "  ┣━ Format: "
if [ $FORMAT == "mov,mp4,m4a,3gp,3g2,mj2" ]; then
	echo -e "$GREEN$FORMAT ✓$RESET"
else
	echo -e "$RED$FORMAT X$RESET"
fi
echo -ne "  ┣━ Video streams: "
if [ $V_AMMOUNT == "1" ]; then
	echo -e "$GREEN$V_AMMOUNT ✓$RESET"
else
	echo -e "$RED$V_AMMOUNT X$RESET"
fi
echo -ne "  ┣━ Audio streams: "
if [ $A_AMMOUNT == "1" ] || [ $A_AMMOUNT == "2" ]; then
	echo -e "$GREEN$A_AMMOUNT ✓$RESET"
else
	echo -e "$RED$A_AMMOUNT X$RESET"
fi
echo -ne "  ┣━ Subtitle streams: "
if [ $S_AMMOUNT == "0" ]; then
	echo -e "$GREEN$S_AMMOUNT ✓$RESET"
else
	echo -e "$RED$S_AMMOUNT X$RESET"
fi
echo -ne "  ┣━ Data streams: "
if [ $D_AMMOUNT == "0" ]; then
	echo -e "$GREEN$D_AMMOUNT ✓$RESET"
else
	echo -e "$GRAY$D_AMMOUNT ?$RESET"
fi
echo -ne "  ┣━ Attachment streams: "
if [ $T_AMMOUNT == "0" ]; then
	echo -e "$GREEN$T_AMMOUNT ✓$RESET"
else
	echo -e "$RED$T_AMMOUNT X$RESET"
fi
echo -ne "  ┣━ Video Codec: "
if [ $V_CODEC == "h264" ]; then
	echo -e "$GREEN$V_CODEC ✓$RESET"
else
	echo -e "$RED$CODEC X$RESET"
fi
echo -ne "  ┣━ Audio Codec: "
if [ $A_CODEC == "aac" ]; then
	echo -e "$GREEN$A_CODEC ✓$RESET"
else
	echo -e "$RED$A_CODEC X$RESET"
fi
echo -ne "  ┣━ Video Pixel Format: "
if [ $V_PIXFMT == "yuv420p" ]; then
	echo -e "$GREEN$V_PIXFMT ✓$RESET"
else
	echo -e "$RED$V_PIXFMT X$RESET"
fi
echo -ne "  ┣━ Optimized for streaming:"
if [ "$IS_FAST_START" != "" ]; then
	echo -e "$GREEN Yes ✓$RESET"
else
	echo -e "$RED No X$RESET"
fi
echo -e  "  ┃$BLUE Subtitles$RESET"
if [ $S_FILES == "0" ]; then
	echo -e "  ┣━ $RED Not found$RESET"
else
	echo -e "  ┣━ $GREEN Found ($S_FILES)$RESET"
fi
echo -e  "  ┃$BLUE Thumbnail$RESET"
if [ $T_FILES == "0" ]; then
	echo -e "  ┗━ $RED Not found$RESET"
else
	echo -e "  ┗━ $GREEN Found$RESET"
fi
echo -e  "  ┃$BLUE Chapters$RESET"
if [ $C_FILES == "0" ]; then
	echo -e "  ┗━ $RED Not found$RESET"
else
	echo -e "  ┗━ $GREEN Found$RESET"
fi
echo -e  "  ┃$BLUE Stats$RESET"
if [ $ST_FILES == "0" ]; then
	echo -e "  ┗━ $RED Not found$RESET"
else
	echo -e "  ┗━ $GREEN Found$RESET"
fi
