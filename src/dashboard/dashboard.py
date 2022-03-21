import feedparser, re, subprocess
from os import system, path
from util.general import setInterval, colorize
from ui.main import printMainUI
from ui.jobs import printJobsUI
from step.transcode import stepTranscode
from job.download import DownloadJob
from job.transcoding_create import TranscodingCreateJob
from job.upload import UploadJob
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
        self.jobCollections.append(jobCollection)
        self.checkJobs()
    
    def checkJobs(self):
        currentJobTypes = []
        for jobCollection in self.jobCollections:
            if jobCollection.currentJob != None:
                if jobCollection.currentJob.is_alive():
                    currentJobTypes.append(jobCollection.currentJob.jobType)
                else:
                    jobCollection.completedJobs.append(jobCollection.currentJob)
                    jobCollection.currentJob = None
                continue
            
            if len(jobCollection.jobs) < 1:
                continue
            firstJob = jobCollection.jobs[0]

            if firstJob.jobType == "transcodingCreate":
                jobCollection.jobs.remove(firstJob)
                jobCollection.currentJob = firstJob
                jobCollection.currentJob.start()
            elif "download" not in currentJobTypes and firstJob.jobType == "download":
                jobCollection.jobs.remove(firstJob)
                jobCollection.currentJob = firstJob
                jobCollection.currentJob.start()
                currentJobTypes.append("download")
            elif "transcoding" not in currentJobTypes and firstJob.jobType == "transcoding":
                jobCollection.jobs.remove(firstJob)
                jobCollection.currentJob = firstJob
                jobCollection.currentJob.start()
                currentJobTypes.append("transcoding")
            elif "torrent" not in currentJobTypes and firstJob.jobType == "torrent":
                jobCollection.jobs.remove(firstJob)
                jobCollection.currentJob = firstJob
                jobCollection.currentJob.start()
                currentJobTypes.append("torrent")
            elif "upload" not in currentJobTypes and firstJob.jobType == "upload":
                jobCollection.jobs.remove(firstJob)
                jobCollection.currentJob = firstJob
                jobCollection.currentJob.start()
                currentJobTypes.append("upload")

    def loadJobs(self):
        entries = subprocess.getoutput(f'find /usr/src/nyananime/jobs/ -type f -name "*.conf" -printf "%P\\n" | sort').split("\n")
        for entry in entries:
            with open(f"/usr/src/nyananime/jobs/{entry}") as f:
                jobLines = f.readlines()
                animeID = jobLines[0].strip()
                episodeIndex = int(jobLines[1].strip())
                torrentLink = jobLines[2].strip()
                jobStatus = jobLines[3].strip()
                if jobStatus != "finished":
                    print(f"Adding a job (episode {colorize('gray', episodeIndex)} of {colorize('gray', animeID)}, source: {colorize('gray', torrentLink)})")
                    collection = JobCollection(f"New episodes job for '{animeID}'", [])
                    collection.jobs = [DownloadJob(animeID, torrentLink), TranscodingCreateJob(animeID, episodeIndex, collection), UploadJob(animeID)]
                    self.addJobCollection(collection)

    def refreshRSS(self):
        self.rssFeeds = []
        if path.exists(f"/usr/src/nyananime/rss/feeds.conf"):
            with open(f'/usr/src/nyananime/rss/feeds.conf') as f:
                rssLines = f.readlines()
                for i in range(len(rssLines)):
                    self.rssFeeds.append(feedparser.parse(rssLines[i]))

        self.rssFilters = []
        if path.exists(f"/usr/src/nyananime/rss/filters.conf"):
            with open(f'/usr/src/nyananime/rss/filters.conf') as f:
                rssLines = f.readlines()
                for i in range(0, len(rssLines), 2):
                    self.rssFilters.append({ "id": rssLines[i].strip()[1:-1], "regex": rssLines[i + 1].strip() })

        for i in range(len(self.rssFeeds)):
            feed = self.rssFeeds[i]
            for j in range(len(feed.entries)):
                entry = feed.entries[j]
                for k in range(len(self.rssFilters)):
                    rssFilter = self.rssFilters[k]
                    match = re.search(rssFilter["regex"], entry.title)
                    if match != None:
                        # TODO: Support stupid animes which tag with floating points
                        episodeIndex = int(match.group(1))
                        if not path.exists(f"/usr/src/nyananime/jobs/{rssFilter['id']}/{episodeIndex}.conf"):
                            system(f"mkdir -p /usr/src/nyananime/jobs/{rssFilter['id']}")
                            with open(f"/usr/src/nyananime/jobs/{rssFilter['id']}/{episodeIndex}.conf", "w") as f:
                                print(f"Creating a job (episode {colorize('gray', episodeIndex + 1)} of {colorize('gray', rssFilter['id'])}, link: {colorize('gray', entry.link)})...")
                                f.writelines([rssFilter["id"] + "\n", str(episodeIndex) + "\n", entry.link + "\n", "unfinished"])

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
        self.refreshRSS()
        print("Loading jobs...")
        self.loadJobs()

        while 1:
            printMainUI(self)

dashboard = Dashboard()