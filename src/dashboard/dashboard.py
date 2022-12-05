import feedparser, re, subprocess
from os import system, path
from util.general import setInterval, colorize
from ui.main import printMainUI
from ui.jobs import printJobsUI
from job.types.download import DownloadJob
from job.types.transcoding_create import TranscodingCreateJob
from job.types.upload import UploadJob
from job.collection import JobCollection

class Dashboard:
    def __init__(self):
        self.jobCollections = []
        self.jobsUIEnabled = False
        self.jobsUIShowCompleted = True
        self.jobsUICollapse = False
        self.rssFeeds = []
        self.rssFilters = []
        self.run()
        
    def asyncRun(self):
        if self.jobsUIEnabled == True:
            printJobsUI(self)

        self.checkJobs()

    def addJobCollection(self, jobCollection):
        # TODO: Support saving regular jobs
        self.jobCollections.append(jobCollection)
        self.checkJobs()
    
    def checkJobs(self):
        jobTypes = ["download", "transcodingCreate", "transcoding", "torrent", "upload"]
        currentJobTypes = []
        for jobCollection in self.jobCollections:
            if jobCollection.status != "working":
                continue

            # TODO: Support figuring out if a job failed, cancelling dependant ones
            if jobCollection.currentJob != None:
                if jobCollection.currentJob.is_alive():
                    currentJobTypes.append(jobCollection.currentJob.jobType)
                    continue
                else:
                    if jobCollection.currentJob.jobOnComplete != None:
                        jobCollection.currentJob.jobOnComplete()
                    jobCollection.completedJobs.append(jobCollection.currentJob)
                    jobCollection.currentJob = None
            
            if len(jobCollection.jobs) < 1:
                jobCollection.status = "completed"
                if jobCollection.onComplete != None:
                    jobCollection.onComplete()
                continue

            job = jobCollection.jobs[0]
            for jobType in jobTypes:
                if jobType not in currentJobTypes and job.jobType == jobType:
                    jobCollection.jobs.remove(job)
                    jobCollection.currentJob = job
                    jobCollection.currentJob.start()
                    currentJobTypes.append(jobType)

    def changeJobStatus(self, animeID, episodeIndex, status):
        lines = []
        with open(f"/usr/src/nyananime/jobs/{animeID}/{episodeIndex}.conf") as f:
            lines = f.readlines()
        lines[3] = status
        with open(f"/usr/src/nyananime/jobs/{animeID}/{episodeIndex}.conf", "w") as f:
            f.writelines(lines)

    def loadJobs(self):
        entries = subprocess.getoutput(f'find /usr/src/nyananime/jobs/ -type f -name "*.conf" -printf "%P\\n" | sort').split("\n")
        for entry in entries:
            if entry == "": continue
            with open(f"/usr/src/nyananime/jobs/{entry}") as f:
                jobLines = f.readlines()
                animeID = jobLines[0].strip()
                episodeIndex = int(jobLines[1].strip())
                torrentLink = jobLines[2].strip()
                jobStatus = jobLines[3].strip()
                if jobStatus != "finished":
                    print(f"Adding a job (episode {colorize('gray', episodeIndex + 1)} of {colorize('gray', animeID)}, source: {colorize('gray', torrentLink)})")
                    collection = JobCollection(f"New episodes job for '{animeID}/{episodeIndex}'", [])
                    if jobStatus == "download":
                        job = DownloadJob(animeID, episodeIndex, torrentLink)
                        job.jobOnComplete = lambda: self.changeJobStatus(animeID, episodeIndex, "transcode")  # type: ignore
                        collection.jobs.append(job)
                    if jobStatus == "download" or jobStatus == "transcode":
                        job = TranscodingCreateJob(animeID, episodeIndex, episodeIndex, collection)
                        job.jobOnComplete = lambda: self.changeJobStatus(animeID, episodeIndex, "upload")  # type: ignore
                        collection.jobs.append(job)
                    if jobStatus == "download" or jobStatus == "transcode" or jobStatus == "upload":
                        job = UploadJob(animeID, episodeIndex)
                        job.jobOnComplete = lambda: self.changeJobStatus(animeID, episodeIndex, "finished")  # type: ignore
                        collection.jobs.append(job)
                    self.addJobCollection(collection)

    def loadRSS(self):
        self.rssFeeds = []
        if path.exists(f"/usr/src/nyananime/rss/feeds.conf"):
            with open(f'/usr/src/nyananime/rss/feeds.conf') as f:
                rssLines = f.readlines()
                for i in range(len(rssLines)):
                    if rssLines[i].startswith("#"):
                        continue
                    self.rssFeeds.append(feedparser.parse(rssLines[i]))

        self.rssFilters = []
        if path.exists(f"/usr/src/nyananime/rss/filters.conf"):
            with open(f'/usr/src/nyananime/rss/filters.conf') as f:
                rssLines = f.readlines()
                i = 0
                for j in range(len(rssLines)):
                    if i + j >= len(rssLines) or rssLines[i + j].startswith("#"):
                        continue
                    self.rssFilters.append({ "id": rssLines[i + j].strip()[1:-1], "regex": rssLines[i + j + 1].strip() })
                    i += 1

    def createRSSJobs(self, dry=False):
        jobs = []
        for i in range(len(self.rssFeeds)):
            feed = self.rssFeeds[i]
            for j in range(len(feed.entries)):
                entry = feed.entries[j]
                for k in range(len(self.rssFilters)):
                    rssFilter = self.rssFilters[k]
                    match = re.search(rssFilter["regex"], entry.title)
                    if match != None:
                        # TODO: Support stupid animes which tag with floating points
                        episodeIndex = int(match.group(1)) - 1
                        if not path.exists(f"/usr/src/nyananime/jobs/{rssFilter['id']}/{episodeIndex}.conf"):
                            jobs.append(f"-> Episode {colorize('gray', episodeIndex + 1)} of {colorize('gray', rssFilter['id'])} (link: {colorize('gray', entry.link)})...")
                            if not dry:
                                system(f"mkdir -p /usr/src/nyananime/jobs/{rssFilter['id']}")
                                with open(f"/usr/src/nyananime/jobs/{rssFilter['id']}/{episodeIndex}.conf", "w") as f:
                                    print(f"Creating a job (episode {colorize('gray', episodeIndex + 1)} of {colorize('gray', rssFilter['id'])}, link: {colorize('gray', entry.link)})...")
                                    f.writelines([rssFilter["id"] + "\n", str(episodeIndex) + "\n", entry.link + "\n", "download"])

        return jobs

    def run(self):
        setInterval(1, self.asyncRun)
        if path.exists(f"/usr/src/nyanime/ssh/id_rsa"):
            system("eval $(ssh-agent)")
            system("ssh-add /usr/src/nyanime/ssh/id_rsa")
        
        system("mkdir -p /usr/src/nyananime/src-episodes")
        system("mkdir -p /usr/src/nyananime/dest-episodes")
        system("mkdir -p /usr/src/nyananime/rss")
        system("mkdir -p /usr/src/nyananime/jobs")
        system("mkdir -p /usr/src/nyananime/torrents")

        system("clear")
        print("Loading RSS...")
        self.loadRSS()

        while 1:
            printMainUI(self)

dashboard = Dashboard()