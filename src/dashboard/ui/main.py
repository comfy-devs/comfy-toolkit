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
        print("1) Complete (combines all steps)")
        print("2) Transcode (used to transcode anime)")
        print("3) Create torrent (used to create a torrent for an anime)")
        print("4) Upload (used to upload anime)")
        print("5) Back")
        selection = input("> Selection? [5]: ")
        selection = "5" if selection == "" else selection

        if selection == "1":
            system("clear")
            print(f'{colorize("gray", f"Nyan Anime Toolkit - All")}')
            opt_id = input("> Anime ID? (ID from anilist.co): ")

            # Poster is needed for the torrent
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
            dashboard.addJobCollection(JobCollection(f"Complete job for '{opt_id}'", jobs))
        if selection == "2":
            system("clear")
            print(f'{colorize("gray", f"Nyan Anime Toolkit - Transcode")}')
            opt_id = input("> Anime ID? (ID from anilist.co): ")
            stepSelect(dashboard, opt_id)
            dashboard.addJobCollection(JobCollection(f"Transcoding job for '{opt_id}'", stepTranscode(dashboard, opt_id)))
        elif selection == "3":
            system("clear")
            print(f'{colorize("gray", f"Nyan Anime Toolkit - Torrent")}')
            opt_id = input("> Anime ID? (ID from anilist.co): ")
            dashboard.addJobCollection(JobCollection(f"Torrent job for '{opt_id}'", [TorrentJob(opt_id)]))
        elif selection == "4":
            system("clear")
            print(f'{colorize("gray", f"Nyan Anime Toolkit - Upload")}')
            opt_id = input("> Anime ID? (ID from anilist.co): ")
            dashboard.addJobCollection(JobCollection(f"Upload job for '{opt_id}'", [UploadJob(opt_id)]))
    elif selection == "3":
        system("clear")
        print(f'{colorize("gray", f"Nyan Anime Toolkit - Other")}')
        print("1) Extra (used for extra post-processing)")
        print("2) Back")
        selection = input("> Selection? [1]: ")
        selection = "1" if selection == "" else selection

        if selection == "1":
            system("clear")
            print(f'{colorize("gray", f"Nyan Anime Toolkit - Extra")}')
            opt_id = input("> Anime ID? (ID from anilist.co): ")
            opt_mal_id = input("> Anime ID? (ID from myanimelist.net): ")
            stepExtra(opt_id, opt_mal_id)
    elif selection == "4":
        exit(0)