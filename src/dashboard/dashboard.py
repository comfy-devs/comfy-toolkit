from os import system
from util.general import setInterval, colorize
from ui.main import printMainUI
from ui.jobs import printJobsUI

class Dashboard:
    def __init__(self):
        self.jobCollections = []
        self.jobsUIEnabled = False
        self.jobsUIShowCompleted = True
        self.jobsUICollapse = False
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

            if "transcoding" not in currentJobTypes and firstJob.jobType == "transcoding":
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

    def run(self):
        setInterval(1, self.asyncRun)
        system("mkdir -p /usr/src/nyananime/src-episodes")
        system("mkdir -p /usr/src/nyananime/dest-episodes")

        while 1:
            printMainUI(self)

dashboard = Dashboard()