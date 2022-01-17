# /bin/bash
# Additional cleaning of VTT subtitles

cd ../clean-vtt
yarn process "$1/subs_en.vtt" "$1/subs_en_out.vtt"
mv -f "$1/subs_en_out.vtt" "$1/subs_en.vtt"
cd ../scripts
