from os import system
from util.general import colorize
from job.torrent import TorrentJob

def stepTorrent(dashboard):
    system("clear")
    print(f'{colorize("gray", f"Nyan Anime Toolkit - Torrent")}')
    opt_id = input("> Anime ID? (ID from anilist.co): ")

    job = TorrentJob("torrent")
    job.setup(opt_id)
    dashboard.addJob(job)