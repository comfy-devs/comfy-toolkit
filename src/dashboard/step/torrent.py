from os import system
from util.general import colorize
from job.torrent import TorrentJob

def stepTorrent(dashboard):
    system("clear")
    print(f'{colorize("gray", f"Nyan Anime Toolkit - Torrent")}')
    opt_id = input("> Anime ID? (ID from anilist.co): ")

    job = TorrentJob("torrent", f"Creating a torrent for {opt_id}")
    job.setup(opt_id)
    dashboard.jobs.append(job)