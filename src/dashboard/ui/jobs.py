import functools
from os import system
from util.general import colorize

def printJob(job, status, color="reset"):
    jobType = "{:<12}".format(job.jobType[:12])
    jobName = "{:<72}".format(job.jobName[:72])
    jobStatus = "{:<12}".format(status[:12])
    jobProgress = str(job.jobProgress) + "%"
    jobProgress = "{:<8}".format(jobProgress[:8])
    jobSpeed = "{:<8}".format(job.jobSpeed[:8])
    print(f'|- {colorize(color, f"{jobType} | {jobName} | {jobStatus} | {jobProgress} | {jobSpeed}")}')

def printJobsUI(dashboard):
    n = functools.reduce(lambda acc, curr: acc + len(curr.jobs) + (1 if curr.currentJob != None else 0), dashboard.jobCollections, 0)
    if dashboard.jobsUIShowCompleted:
        n += functools.reduce(lambda acc, curr: acc + len(curr.completedJobs), dashboard.jobCollections, 0)

    system("clear")
    print(colorize("gray", f'Nyan Anime Toolkit - Jobs ({n})'))

    for jobCollection in dashboard.jobCollections:
        print(f"| {colorize('bright_blue' if jobCollection.currentJob != None else ('bright_green' if len(jobCollection.jobs) == 0 else 'white'), jobCollection.name)}")
        if dashboard.jobsUICollapse:
            continue

        if jobCollection.currentJob != None:
            printJob(jobCollection.currentJob, "in progress", "bright_blue")
        for job in jobCollection.jobs:
            printJob(job, "waiting")
        if dashboard.jobsUIShowCompleted:
            for job in jobCollection.completedJobs:
                printJob(job, "completed", "bright_green")
        print("")
    
    print(f"1) {'Hide' if dashboard.jobsUIShowCompleted else 'Show'} completed jobs")
    print(f"2) {'Uncollapse' if dashboard.jobsUICollapse else 'Collapse'} jobs")
    print("3) Back")
    print("> Selection? [3]: ")