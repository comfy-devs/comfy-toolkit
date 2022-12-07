import subprocess
from util.general import colorize
from job.types.transcoding import TranscodingJob

# TODO: fix this for single episodes
def stepTranscode(dashboard, opt_id, i=0):
    opt_codec = input("> Encoding codec? (x264/vp9) [x264]: ")
    opt_codec = "x264" if opt_codec == "" else opt_codec

    opt_min_bitrate = ""
    opt_bitrate = ""
    opt_max_bitrate = ""
    if opt_codec == "vp9":
        entries = list(filter(None, subprocess.getoutput(f'find {dashboard.path}/dest-episodes/{opt_id}/ -type f -name "*.mp4" -printf "%P\\n" | sort').split("\n")))
        all_bitrate = 0
        if len(entries) > 0:
            print(f"Listing bitrates of previous transcodes ({len(entries)})...")
            for entry in entries:
                v_bitrate = subprocess.getoutput(f'ffprobe -i "{dashboard.path}/dest-episodes/{opt_id}/{entry}" -v quiet -select_streams v:0 -show_entries stream=bit_rate -hide_banner -of default=noprint_wrappers=1:nokey=1')
                try:
                    v_bitrate = round(float(v_bitrate) / 1000)
                    all_bitrate += v_bitrate
                    print(f'Bitrate for episode \'{colorize("gray", entry)}\': {v_bitrate} kb/s')
                except:
                    print(f'Bitrate for episode \'{colorize("gray", entry)}\': ?? kb/s')
            all_bitrate = round(all_bitrate / len(entries))
            print(f'Average bitrate for {colorize("gray", len(entries))} episodes: {all_bitrate} kb/s')
        else:
            print("No previous transcodes found! It is recommended you run x264 transcodes first in order to more accurately pick the right bitrate for VP9.")

        opt_min_bitrate = input("> Minimal bitrate? (recommended: 550k) [550k]: ")
        opt_min_bitrate = "550k" if opt_min_bitrate == "" else opt_min_bitrate
        opt_bitrate_r = "1600k" if all_bitrate == 0 else f"{round(all_bitrate * 0.55)}k"
        opt_bitrate = input(f"> Target bitrate? (recommended: (average * 0.55)k or 1600k) [{opt_bitrate_r}]: ")
        opt_bitrate = opt_bitrate_r if opt_bitrate == "" else opt_bitrate
        opt_max_bitrate_r = "2210k" if all_bitrate == 0 else f"{round(all_bitrate * 0.65)}k"
        opt_max_bitrate = input(f"> Maximal bitrate? (recommended: (average * 0.65)k or 2210k) [{opt_max_bitrate_r}]: ")
        opt_max_bitrate = opt_max_bitrate_r if opt_max_bitrate == "" else opt_max_bitrate

    jobs = []
    entries = subprocess.getoutput(f'find {dashboard.path}/src-episodes/{opt_id}/ -type f -name "*.mkv" -printf "%P\\n" | sort').split("\n")
    for entry in entries:
        jobs.append(TranscodingJob(dashboard, opt_id, i, f"{dashboard.path}/src-episodes/{opt_id}/{entry}", opt_codec, [opt_min_bitrate, opt_bitrate, opt_max_bitrate]))
        i += 1
    
    return jobs