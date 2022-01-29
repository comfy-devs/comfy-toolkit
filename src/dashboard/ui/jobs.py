from os import system
from util import getColor

def printJob(job, color="reset"):
    jobType = "{:<10}".format(job.jobType[:10])
    jobName = "{:<64}".format(job.jobName[:64])
    jobStatus = "{:<10}".format(job.jobStatus[:10])
    jobProgress = str(job.jobProgress) + "%"
    jobProgress = "{:<10}".format(jobProgress[:10])
    print(f'{getColor(color)}{jobType} | {jobName} | {jobStatus} | {jobProgress}{getColor("reset")}')

def printJobsUI(dashboard):
    n = len(dashboard.jobs)
    if dashboard.currentJob != None:
        n += 1
    if dashboard.jobsUIShowCompleted:
        n += len(dashboard.completedJobs)

    system("clear")
    print(f'{getColor("gray")}Nyan Anime Toolkit - Jobs ({n}){getColor("reset")}')
    print(f'{getColor("gray")}{"{:<10}".format("Type")} | {"{:<64}".format("Name")} | {"{:<10}".format("Status")} | {"{:<10}".format("Progress")}{getColor("reset")}')
    
    if dashboard.currentJob != None:
        printJob(dashboard.currentJob, "bright_blue")
    for job in dashboard.jobs:
        printJob(job)
    if dashboard.jobsUIShowCompleted:
        for job in dashboard.completedJobs:
            printJob(job, "bright_green")
    
    print("")
    print("1) Toggle completed jobs")
    print("2) Back")
    print("> Selection? [2]: ")