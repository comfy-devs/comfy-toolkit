from os import system
from util.general import colorize
from job.upload import UploadJob

def stepUpload(dashboard):
    system("clear")
    print(f'{colorize("gray", f"Nyan Anime Toolkit - Upload")}')
    opt_id = input("> Anime ID? (ID from anilist.co): ")

    job = UploadJob("upload", f"Uploading files from {opt_id}")
    job.setup(opt_id)
    dashboard.jobs.append(job)