import subprocess
from os import system, path
from util.general import colorize

def stepUpload():
    system("clear")
    print(f'{colorize("gray", f"Nyan Anime Toolkit - Upload")}')
    opt_id = input("> Anime ID? (ID from anilist.co): ")
    opt_move = input("> Move all files onto a server folder? (y/n) [y]: ")
    opt_move = "y" if opt_move == "" else opt_move

    if opt_move == "y":
        i = 0
        entries = subprocess.getoutput(f"LC_COLLATE=C ls /usr/src/nyananime/dest-episodes/{opt_id}").split("\n")
        for entry in entries:
            print(f'Moving episode {colorize("gray", i)}')
            system(f'mkdir -p "/usr/src/nyananime/server-video/{opt_id}/{i}"')
            system(f'mkdir -p "/usr/src/nyananime/server-image/{opt_id}/{i}"')

            if path.exists(f"/usr/src/nyananime/dest-episodes/{opt_id}/{i}/ep_low.mp4"):
                system(f'mv "/usr/src/nyananime/dest-episodes/{opt_id}/{i}/ep_low.mp4" "/usr/src/nyananime/server-video/{opt_id}/{i}/ep_low.mp4"')

            if path.exists(f"/usr/src/nyananime/dest-episodes/{opt_id}/{i}/ep_med.mp4"):
                system(f'mv "/usr/src/nyananime/dest-episodes/{opt_id}/{i}/ep_med.mp4" "/usr/src/nyananime/server-video/{opt_id}/{i}/ep_med.mp4"')

            if path.exists(f"/usr/src/nyananime/dest-episodes/{opt_id}/{i}/ep_high.mp4"):
                system(f'mv "/usr/src/nyananime/dest-episodes/{opt_id}/{i}/ep_high.mp4" "/usr/src/nyananime/server-video/{opt_id}/{i}/ep_high.mp4"')

            if path.exists(f"/usr/src/nyananime/dest-episodes/{opt_id}/{i}/ep_vp9.webm"):
                system(f'mv "/usr/src/nyananime/dest-episodes/{opt_id}/{i}/ep_vp9.webm" "/usr/src/nyananime/server-video/{opt_id}/{i}/ep_vp9.webm"')
           
            if path.exists(f"/usr/src/nyananime/dest-episodes/{opt_id}/{i}/subs_en.vtt"):
                system(f'mv "/usr/src/nyananime/dest-episodes/{opt_id}/{i}/subs_en.vtt" "/usr/src/nyananime/server-video/{opt_id}/{i}/subs_en.vtt"')

            if path.exists(f"/usr/src/nyananime/dest-episodes/{opt_id}/{i}/thumbnail.webp"):
                system(f'mv "/usr/src/nyananime/dest-episodes/{opt_id}/{i}/thumbnail.webp" "/usr/src/nyananime/server-image/{opt_id}/{i}/thumbnail.webp"')

            if path.exists(f"/usr/src/nyananime/dest-episodes/{opt_id}/{i}/chapters.json"):
                system(f'mv "/usr/src/nyananime/dest-episodes/{opt_id}/{i}/chapters.json" "/usr/src/nyananime/server-video/{opt_id}/{i}/chapters.json"')

            if path.exists(f"/usr/src/nyananime/dest-episodes/{opt_id}/{i}/stats.json"):
                system(f'mv "/usr/src/nyananime/dest-episodes/{opt_id}/{i}/stats.json" "/usr/src/nyananime/server-video/{opt_id}/{i}/stats.json"')

            system(f'rmdir "/usr/src/nyananime/dest-episodes/{opt_id}/{i}"')
            i += 1

        if path.exists(f"/usr/src/nyananime/dest-episodes/{opt_id}/poster.webp"):
            system(f'mv "/usr/src/nyananime/dest-episodes/{opt_id}/poster.webp" "/usr/src/nyananime/server-image/{opt_id}/poster.webp"')

        if path.exists(f"/usr/src/nyananime/dest-episodes/{opt_id}/series.torrent"):
            system(f'mv "/usr/src/nyananime/dest-episodes/{opt_id}/series.torrent" "/usr/src/nyananime/server-video/{opt_id}/series.torrent"')

        system(f'rmdir "/usr/src/nyananime/dest-episodes/{opt_id}"')