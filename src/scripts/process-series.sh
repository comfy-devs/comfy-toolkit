# /bin/bash
# All-in-one for processing series

OIFS="$IFS"
IFS=$'\n'

GRAY="\033[0;37m"
RESET="\033[0m"

mkdir -p /usr/src/nyananime/src-episodes
mkdir -p /usr/src/nyananime/dest-episodes

refresh() {
	S_FILES=$(find /usr/src/nyananime/src-episodes -name *.mkv | wc -l)
	D_FILES=$(find /usr/src/nyananime/dest-episodes -name *.mp4 | wc -l)
}

step_select() {
	clear
	echo -e "$(echo $GRAY)Nyan Anime Toolkit - Select$RESET"

	if [ ! $S_FILES == "0" ]; then
		read -p "> Existing source files found! Delete them? (y/n) [n]: " OPT_DELETE_SRC
		OPT_DELETE_SRC=${OPT_DELETE_SRC:-n}
		if [ $OPT_DELETE_SRC == "y" ]; then
			echo "Deleting source files..."
			rm -rf /usr/src/nyananime/src-episodes/*
			refresh
		fi
	fi

	if [ $S_FILES == "0" ]; then
		read -p "> Anime selection method? (local) [local]: " OPT_SEL_METHOD
		OPT_SEL_METHOD=${OPT_SEL_METHOD:-local}
		case $OPT_SEL_METHOD in
			local)
				OPT_SEL_SRC=$(mktemp)
				ranger --choosedir="$OPT_SEL_SRC" 1>&2
				OPT_SEL_SRC=$(cat $OPT_SEL_SRC)
				rm -rf /usr/src/nyananime/src-episodes; ln -sf $OPT_SEL_SRC /usr/src/nyananime/src-episodes
			;;
		esac
		refresh
	fi

	if [ ! $D_FILES == "0" ]; then
		read -p "> Existing destination files found! Delete them? (y/n) [n]: " OPT_DELETE_DEST
		OPT_DELETE_DEST=${OPT_DELETE_DEST:-n}
		if [ $OPT_DELETE_DEST == "y" ]; then
			echo "Deleting destination files..."
			rm -rf /usr/src/nyananime/dest-episodes/*
			refresh
		fi
	fi
}

step_transcode() {
	clear
	echo -e "$(echo $GRAY)Nyan Anime Toolkit - Transcode$RESET"

	read -p "> Encoding quality? (low/med/high/vp9) [high]: " OPT_QUALITY
	OPT_QUALITY=${OPT_QUALITY:-high}
	case $OPT_QUALITY in
		low)
			D_SCRIPT="ffmpeg-video-low-x264.sh"
			D_VFILE="ep_low.mp4"
		;;
		med)
			D_SCRIPT="ffmpeg-video-med-x264.sh"
			D_VFILE="ep_med.mp4"
		;;
		high)
			D_SCRIPT="ffmpeg-video-high-x264.sh"
			D_VFILE="ep_high.mp4"
		;;
		vp9)
			echo "Listing bitrates of previous transcodes..."
			for entry in `LC_COLLATE=C ls /usr/src/nyananime/dest-episodes`
			do
				V_FILE=$(find "/usr/src/nyananime/dest-episodes/$entry" -name *.mp4)
				V_BITRATE=$(ffprobe -i "$V_FILE" -v quiet -select_streams v:0 -show_entries stream=bit_rate -hide_banner -of default=noprint_wrappers=1:nokey=1)
				A_BITRATE=$(ffprobe -i "$V_FILE" -v quiet -select_streams a:0 -show_entries stream=bit_rate -hide_banner -of default=noprint_wrappers=1:nokey=1)
				S_BITRATE=$(echo "scale=3;($V_BITRATE+$A_BITRATE)/1000000" | bc)
				echo -e "Bitrate for episode $GRAY'$entry'$RESET: $S_BITRATE Mb/s ($V_BITRATE/$A_BITRATE)"
			done

			read -p "> Minimal bitrate? [550k]: " OPT_MIN_BITRATE
			OPT_MIN_BITRATE=${OPT_MIN_BITRATE:-550k}
			read -p "> Target bitrate? [1600k]: " OPT_BITRATE
			OPT_BITRATE=${OPT_BITRATE:-1600k}
			read -p "> Maximal bitrate? [2210k]: " OPT_MAX_BITRATE
			OPT_MAX_BITRATE=${OPT_MAX_BITRATE:-2210k}

			D_SCRIPT="ffmpeg-video-vp9.sh"
			D_VFILE="ep_vp9.webm"
		;;
	esac

	I=0
	for entry in `LC_COLLATE=C ls /usr/src/nyananime/src-episodes`
	do
		echo -e "Processing episode $GRAY$(($I+1))/$S_FILES$RESET..."
		mkdir -p "/usr/src/nyananime/dest-episodes/$I"

		if [ ! -f "/usr/src/nyananime/dest-episodes/$I/$D_VFILE" ]; then
			echo -e "┣━ Transcoding episode $GRAY'$entry'$RESET..."
			./$D_SCRIPT "/usr/src/nyananime/src-episodes/$entry" "/usr/src/nyananime/dest-episodes/$I" $OPT_MIN_BITRATE $OPT_BITRATE $OPT_MAX_BITRATE
		else
			echo -e "┣━ Transcoding of $GRAY'$entry'$RESET already done. Skipping..."
		fi
		if [ ! -f "/usr/src/nyananime/dest-episodes/$I/subs_en.vtt" ]; then
			echo -e "┣━ Generating subtitles for $GRAY'$entry'$RESET..."
			./ffmpeg-subs.sh "/usr/src/nyananime/src-episodes/$entry" "/usr/src/nyananime/dest-episodes/$I"
			./ffmpeg-subs-clean.sh "/usr/src/nyananime/dest-episodes/$I"
			./ffmpeg-subs-clean-ad.sh "/usr/src/nyananime/dest-episodes/$I"
		else
			echo -e "┣━ Subtitles for $GRAY'$entry'$RESET already generated. Skipping..."
		fi
		if [ ! -f "/usr/src/nyananime/dest-episodes/$I/thumbnail.webp" ]; then
			echo -e "┣━ Generating thumbnail for $GRAY'$entry'$RESET..."
			./ffmpeg-thumbnail.sh "/usr/src/nyananime/src-episodes/$entry" "/usr/src/nyananime/dest-episodes/$I"
		else
			echo -e "┣━ Thumbnail for $GRAY'$entry'$RESET already generated. Skipping..."
		fi
		if [ ! -f "/usr/src/nyananime/dest-episodes/$I/chapters.json" ]; then
			echo -e "┣━ Generating chapters for $GRAY'$entry'$RESET..."
			./ffmpeg-chapters.sh "/usr/src/nyananime/src-episodes/$entry" "/usr/src/nyananime/dest-episodes/$I"
		else
			echo -e "┣━ Chapters for $GRAY'$entry'$RESET already generated. Skipping..."
		fi
		if [ ! -f "/usr/src/nyananime/dest-episodes/$I/stats.json" ]; then
			echo -e "┗━ Generating stats for $GRAY'$entry'$RESET..."
			./ffmpeg-stats.sh "/usr/src/nyananime/dest-episodes/$I/$D_VFILE" "/usr/src/nyananime/dest-episodes/$I"
		else
			echo -e "┗━ Stats for $GRAY'$entry'$RESET already generated. Skipping..."
		fi
		
		echo ""
		I=$(($I+1))
	done
}

step_extra() {
	clear
	echo -e "$(echo $GRAY)Nyan Anime Toolkit - Extra$RESET"
	
	read -p "> Download poster? (y/n) [y]: " OPT_POSTER
	OPT_POSTER=${OPT_POSTER:-y}
	if [ $OPT_MOVE == "y" ]; then
		read -p "> Poster URL? (URL from anilist.co): " OPT_POSTER_URL
		wget -O /usr/src/nyananime/dest-episodes/poster_in $OPT_POSTER_URL
		cwebp -q 90 /usr/src/nyananime/dest-episodes/poster_in -o /usr/src/nyananime/dest-episodes/poster.webp
		rm /usr/src/nyananime/dest-episodes/poster_in
	fi
}

step_upload() {
	clear
	echo -e "$(echo $GRAY)Nyan Anime Toolkit - Upload$RESET"

	read -p "> Move all files onto a server folder? (y/n) [y]: " OPT_MOVE
	OPT_MOVE=${OPT_MOVE:-y}
	if [ $OPT_MOVE == "y" ]; then
		read -p "> Anime ID? (ID from anilist.co): " OPT_ID

		I=0
		for entry in `LC_COLLATE=C ls /usr/src/nyananime/dest-episodes`
		do
			echo -e "Moving episode $GRAY$(($I+1))$RESET..."
			mkdir -p "/usr/src/nyananime/server-video/$OPT_ID/$I"
			mkdir -p "/usr/src/nyananime/server-image/$OPT_ID/$I"
			if [ -f "/usr/src/nyananime/dest-episodes/$I/ep_low.mp4" ]; then
				mv "/usr/src/nyananime/dest-episodes/$I/ep_low.mp4" "/usr/src/nyananime/server-video/$OPT_ID/$I/ep_low.mp4"
			fi
			if [ -f "/usr/src/nyananime/dest-episodes/$I/ep_med.mp4" ]; then
				mv "/usr/src/nyananime/dest-episodes/$I/ep_med.mp4" "/usr/src/nyananime/server-video/$OPT_ID/$I/ep_med.mp4"
			fi
			if [ -f "/usr/src/nyananime/dest-episodes/$I/ep_high.mp4" ]; then
				mv "/usr/src/nyananime/dest-episodes/$I/ep_high.mp4" "/usr/src/nyananime/server-video/$OPT_ID/$I/ep_high.mp4"
			fi
			if [ -f "/usr/src/nyananime/dest-episodes/$I/ep_vp9.mp4" ]; then
				mv "/usr/src/nyananime/dest-episodes/$I/ep_vp9.mp4" "/usr/src/nyananime/server-video/$OPT_ID/$I/ep_vp9.mp4"
			fi
			if [ -f "/usr/src/nyananime/dest-episodes/$I/subs_en.vtt" ]; then
				mv "/usr/src/nyananime/dest-episodes/$I/subs_en.vtt" "/usr/src/nyananime/server-video/$OPT_ID/$I/subs_en.vtt"
			fi
			if [ -f "/usr/src/nyananime/dest-episodes/$I/thumbnail.webp" ]; then
				mv "/usr/src/nyananime/dest-episodes/$I/thumbnail.webp" "/usr/src/nyananime/server-image/$OPT_ID/$I/thumbnail.webp"
			fi
			if [ -f "/usr/src/nyananime/dest-episodes/$I/chapters.json" ]; then
				mv "/usr/src/nyananime/dest-episodes/$I/chapters.json" "/usr/src/nyananime/server-video/$OPT_ID/$I/chapters.json"
			fi
			if [ -f "/usr/src/nyananime/dest-episodes/$I/stats.json" ]; then
				mv "/usr/src/nyananime/dest-episodes/$I/stats.json" "/usr/src/nyananime/server-video/$OPT_ID/$I/stats.json"
			fi
			rmdir "/usr/src/nyananime/dest-episodes/$I"
			I=$(($I+1))
		done
		if [ -f "/usr/src/nyananime/dest-episodes/poster.webp" ]; then
			mv "/usr/src/nyananime/dest-episodes/poster.webp" "/usr/src/nyananime/server-image/$OPT_ID/poster.webp"
		fi
	fi
}

refresh
while [ 1 ]
do
	clear
	echo -e "$(echo $GRAY)Nyan Anime Toolkit - Menu$RESET"
	echo "1) All (goes through all options)"
	echo "2) Select (used to select anime for processing)"
	echo "3) Transcode (used to transcode anime)"
	echo "4) Extra (used for extra post-processing)"
	echo "5) Upload (used for uploading onto the server)"
	echo "6) Quit"
	read -p "> Selection? [1]: " SELECTION
	SELECTION=${SELECTION:-1}

	case $SELECTION in
		1)
			step_select
			step_transcode
			step_extra
			step_upload
		;;
		2)
			step_select
		;;
		3)
			step_transcode
		;;
		4)
			step_extra
		;;
		5)
			step_upload
		;;
		6)
			break
		;;
	esac
done
