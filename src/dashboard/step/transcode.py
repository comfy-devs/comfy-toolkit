import subprocess
from os import system
from util import getColor
from job.job import Job

def stepTranscode(dashboard):
    system("clear")
    print(f'{getColor("gray")}Nyan Anime Toolkit - Transcode{getColor("reset")}')
    opt_id = input("> Anime ID? (ID from anilist.co): ")
    opt_quality = input("> Encoding quality? (low/med/high/vp9) [high]: ")
    opt_quality = "high" if opt_quality == "" else opt_quality

    dest_script = ""
    dest_file = ""
    opt_min_bitrate = ""
    opt_bitrate = ""
    opt_max_bitrate = ""
    if opt_quality == "low":
        dest_script = "ffmpeg-video-low-x264.sh"
        dest_file = "ep_low.mp4"
    elif opt_quality == "med":
        dest_script = "ffmpeg-video-med-x264.sh"
        dest_file = "ep_med.mp4"
    elif opt_quality == "high":
        dest_script = "ffmpeg-video-high-x264.sh"
        dest_file = "ep_high.mp4"
    elif opt_quality == "vp9":		
        dest_script = "ffmpeg-video-vp9.sh"
        dest_file = "ep_vp9.webm"

        entries = subprocess.getoutput(f"LC_COLLATE=C ls /usr/src/nyananime/dest-episodes/{opt_id}").split("\n")
        if len(entries) > 0:
            print("Listing bitrates of previous transcodes...")
            for entry in entries:
                v_file = subprocess.getoutput(f'find "/usr/src/nyananime/dest-episodes/{opt_id}/{entry}" -name *.mp4')
                v_bitrate = subprocess.getoutput(f'ffprobe -i "{v_file}" -v quiet -select_streams v:0 -show_entries stream=bit_rate -hide_banner -of default=noprint_wrappers=1:nokey=1')
                try:
                    v_bitrate = round(float(v_bitrate) / 1000000, 2)
                    print(f'Bitrate for episode {getColor("gray")}\'{entry}\'{getColor("reset")}: {v_bitrate} Mb/s')
                except e:
                    print(f'Bitrate for episode {getColor("gray")}\'{entry}\'{getColor("reset")}: ?? Mb/s')

        opt_min_bitrate = input("> Minimal bitrate? (recommended: 550k) [550k]: ")
        opt_min_bitrate = "550k" if opt_min_bitrate == "" else opt_min_bitrate
        opt_bitrate = input("> Target bitrate? (recommended: (average * 0.55)k) [1600k]: ")
        opt_bitrate = "1600k" if opt_bitrate == "" else opt_bitrate
        opt_max_bitrate = input("> Maximal bitrate? (recommended: (average * 0.65)k) [2210k]: ")
        opt_max_bitrate = "2210k" if opt_max_bitrate == "" else opt_max_bitrate

    i = 0
    entries = subprocess.getoutput(f"LC_COLLATE=C ls /usr/src/nyananime/src-episodes/{opt_id}").split("\n")
    for entry in entries:
        job = Job("transcoding", entry)
        job.setupTranscoding(opt_id, i, entry, dest_file, dest_script, [opt_min_bitrate, opt_bitrate, opt_max_bitrate])
        dashboard.jobs.append(job)
        i += 1