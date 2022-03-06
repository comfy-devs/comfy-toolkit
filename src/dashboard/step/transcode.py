import subprocess
from os import system
from util.general import colorize
from job.transcoding import TranscodingJob
from job.collection import JobCollection

def stepTranscode(dashboard, opt_id):
    opt_codec = input("> Encoding codec? (x264/vp9) [x264]: ")
    opt_codec = "x264" if opt_codec == "" else opt_codec

    dest_script = ""
    dest_file = ""
    opt_min_bitrate = ""
    opt_bitrate = ""
    opt_max_bitrate = ""
    if opt_codec == "vp9":
        entries = subprocess.getoutput(f"LC_COLLATE=C ls /usr/src/nyananime/dest-episodes/{opt_id}").split("\n")
        if len(entries) > 0:
            print("Listing bitrates of previous transcodes...")
            for entry in entries:
                v_file = subprocess.getoutput(f'find "/usr/src/nyananime/dest-episodes/{opt_id}/{entry}" -name *.mp4')
                v_bitrate = subprocess.getoutput(f'ffprobe -i "{v_file}" -v quiet -select_streams v:0 -show_entries stream=bit_rate -hide_banner -of default=noprint_wrappers=1:nokey=1')
                try:
                    v_bitrate = round(float(v_bitrate) / 1000000, 2)
                    print(f'Bitrate for episode \'{colorize("gray", entry)}\': {v_bitrate} Mb/s')
                except e:
                    print(f'Bitrate for episode \'{colorize("gray", entry)}\': ?? Mb/s')

        opt_min_bitrate = input("> Minimal bitrate? (recommended: 550k) [550k]: ")
        opt_min_bitrate = "550k" if opt_min_bitrate == "" else opt_min_bitrate
        opt_bitrate = input("> Target bitrate? (recommended: (average * 0.55)k) [1600k]: ")
        opt_bitrate = "1600k" if opt_bitrate == "" else opt_bitrate
        opt_max_bitrate = input("> Maximal bitrate? (recommended: (average * 0.65)k) [2210k]: ")
        opt_max_bitrate = "2210k" if opt_max_bitrate == "" else opt_max_bitrate

    i = 0
    jobs = []
    entries = subprocess.getoutput(f"LC_COLLATE=C ls /usr/src/nyananime/src-episodes/{opt_id}").split("\n")
    for entry in entries:
        jobs.append(TranscodingJob(opt_id, i, entry, opt_codec, [opt_min_bitrate, opt_bitrate, opt_max_bitrate]))
        i += 1
    
    return jobs