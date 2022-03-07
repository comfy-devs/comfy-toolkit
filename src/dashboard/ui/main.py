from os import system
from util.general import colorize
from step.select import stepSelect
from step.transcode import stepTranscode
from step.extra import stepExtra, downloadPoster
from job.torrent import TorrentJob
from job.upload import UploadJob
from job.collection import JobCollection
from util.api import fetchAnilist

def printJobsUISelector(dashboard):
    dashboard.jobsUIEnabled = True
    selection = input("")
    selection = "1" if selection == "" else selection
    if selection == "1":
        dashboard.jobsUIShowCompleted = not dashboard.jobsUIShowCompleted
    elif selection == "2":
        dashboard.jobsUICollapse = not dashboard.jobsUICollapse
    elif selection == "3":
        dashboard.jobsUIEnabled = False
        return
    
    printJobsUISelector(dashboard)

def printMainUI(dashboard):
    system("clear")
    print(f'{colorize("gray", f"Nyan Anime Toolkit - Menu")}')
    print("1) List jobs")
    print("2) Add a job")
    print("3) Other")
    print("4) Quit")
    selection = input("> Selection? [2]: ")
    selection = "2" if selection == "" else selection

    if selection == "1":
        printJobsUISelector(dashboard)
    elif selection == "2":
        system("clear")
        print(f'{colorize("gray", f"Nyan Anime Toolkit - Add a job")}')
        print("1) Complete series (transcodes, creates a torrent and uploads an entire series)")
        print("2) New episodes (trancodes and uploads new episodes)")
        print("3) Only transcode (entire series)")
        print("4) Only transcode (new episodes)")
        print("5) Only create torrent (entire series)")
        print("6) Only upload")
        print("7) Back")
        selection = input("> Selection? [7]: ")
        selection = "7" if selection == "" else selection

        if selection == "1":
            system("clear")
            print(f'{colorize("gray", f"Nyan Anime Toolkit - Complete series")}')
            opt_id = input("> Anime ID? (ID from anilist.co): ")

            # Poster is needed for the torrent
            if not path.exists(f"/usr/src/nyananime/dest-episodes/{opt_id}/poster.webp"):
                media = fetchAnilist(opt_id)
                downloadPoster(opt_id, media["coverImage"]["extraLarge"])

            selection = input("> Process extra data now? [n]: ")
            selection = "n" if selection == "" else selection
            if selection == "y":
                opt_mal_id = input("> Anime ID? (ID from myanimelist.net): ")
                stepExtra(opt_id, opt_mal_id)

            stepSelect(dashboard, opt_id)
            jobs = stepTranscode(dashboard, opt_id)
            jobs.append(TorrentJob(opt_id))
            jobs.append(UploadJob(opt_id))
            dashboard.addJobCollection(JobCollection(f"Complete series job for '{opt_id}'", jobs))
        if selection == "2":
            system("clear")
            print(f'{colorize("gray", f"Nyan Anime Toolkit - New episodes")}')
            opt_id = input("> Anime ID? (ID from anilist.co): ")
            opt_i = input("> First episode index?: ")

            stepSelect(dashboard, opt_id)
            jobs = stepTranscode(dashboard, opt_id, opt_i)
            jobs.append(UploadJob(opt_id))
            dashboard.addJobCollection(JobCollection(f"New episodes job for '{opt_id}'", jobs))
        if selection == "3":
            system("clear")
            print(f'{colorize("gray", f"Nyan Anime Toolkit - Only transcode")}')
            opt_id = input("> Anime ID? (ID from anilist.co): ")
            stepSelect(dashboard, opt_id)
            dashboard.addJobCollection(JobCollection(f"Only transcode job for '{opt_id}'", stepTranscode(dashboard, opt_id)))
        if selection == "4":
            system("clear")
            print(f'{colorize("gray", f"Nyan Anime Toolkit - Only transcode")}')
            opt_id = input("> Anime ID? (ID from anilist.co): ")
            opt_i = input("> First episode index?: ")
            stepSelect(dashboard, opt_id)
            dashboard.addJobCollection(JobCollection(f"Only transcode job for '{opt_id}'", stepTranscode(dashboard, opt_id, opt_i)))
        elif selection == "5":
            system("clear")
            print(f'{colorize("gray", f"Nyan Anime Toolkit - Only torrent")}')
            opt_id = input("> Anime ID? (ID from anilist.co): ")
            dashboard.addJobCollection(JobCollection(f"Only torrent job for '{opt_id}'", [TorrentJob(opt_id)]))
        elif selection == "6":
            system("clear")
            print(f'{colorize("gray", f"Nyan Anime Toolkit - Only upload")}')
            opt_id = input("> Anime ID? (ID from anilist.co): ")
            dashboard.addJobCollection(JobCollection(f"Only upload job for '{opt_id}'", [UploadJob(opt_id)]))
    elif selection == "3":
        system("clear")
        print(f'{colorize("gray", f"Nyan Anime Toolkit - Other")}')
        print("1) Add complete series data")
        print("2) Add new episodes data")
        print("3) Back")
        selection = input("> Selection? [3]: ")
        selection = "3" if selection == "" else selection

        if selection == "1":
            system("clear")
            print(f'{colorize("gray", f"Nyan Anime Toolkit - Add complete series data")}')
            opt_id = input("> Anime ID? (ID from anilist.co): ")
            opt_mal_id = input("> Anime ID? (ID from myanimelist.net): ")
            stepExtra(opt_id, opt_mal_id)
        if selection == "2":
            system("clear")
            print(f'{colorize("gray", f"Nyan Anime Toolkit - Add new episodes data")}')
            opt_id = input("> Anime ID? (ID from anilist.co): ")
            stepExtraEpisodesPartial(opt_id)
    elif selection == "4":
        exit(0)