from os import system
from util.general import colorize

def printJob(job, status, color="reset"):
    jobType = "{:<10}".format(job.jobType[:10])
    jobName = "{:<64}".format(job.jobName[:64])
    jobStatus = "{:<10}".format(status[:10])
    jobProgress = str(job.jobProgress) + "%"
    jobProgress = "{:<10}".format(jobProgress[:10])
    print(f'{colorize(color, f"{jobType} | {jobName} | {jobStatus} | {jobProgress} | {job.jobSpeed}")}')

def printJobsUI(dashboard):
    n = len(dashboard.currentJobs) + len(dashboard.jobs)
    if dashboard.jobsUIShowCompleted:
        n += len(dashboard.completedJobs)

    system("clear")
    print(colorize("gray", f'Nyan Anime Toolkit - Jobs ({n})'))
    print(colorize("gray", f'{"{:<10}".format("Type")} | {"{:<64}".format("Name")} | {"{:<10}".format("Status")} | {"{:<10}".format("Progress")} | {"{:<10}".format("Speed")}'))

    for job in dashboard.currentJobs:
        printJob(job, "in progress", "bright_blue")
    for job in dashboard.jobs:
        printJob(job, "waiting")
    if dashboard.jobsUIShowCompleted:
        for job in dashboard.completedJobs:
            printJob(job, "completed", "bright_green")
    
    print("")
    print(f"1) {'Hide' if dashboard.jobsUIShowCompleted else 'Show'} completed jobs")
    print("2) Back")
    print("> Selection? [2]: ")