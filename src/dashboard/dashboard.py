from os import system
from util.general import setInterval, colorize
from ui.main import printMainUI
from ui.jobs import printJobsUI

class Dashboard:
    def __init__(self):
        self.jobs = []
        self.currentJobs = []
        self.completedJobs = []
        self.jobsUIEnabled = False
        self.jobsUIShowCompleted = True
        self.run()
        
    def asyncRun(self):
        if self.jobsUIEnabled == True:
            printJobsUI(self)

        self.checkJobs()

    def addJob(self, job):
        self.jobs.append(job)
        self.checkJobs()
    
    def checkJobs(self):
        currentTranscodingJob = next(filter(lambda e: e.jobType == "transcoding", self.currentJobs), None)
        if currentTranscodingJob == None:
            availableTranscodingJob = next(filter(lambda e: e.jobType == "transcoding", self.jobs), None)
            if availableTranscodingJob != None:
                self.jobs.remove(availableTranscodingJob)
                self.currentJobs.append(availableTranscodingJob)
                availableTranscodingJob.start()
        elif currentTranscodingJob.is_alive() == False:
            self.completedJobs.append(currentTranscodingJob)
            self.currentJobs.remove(currentTranscodingJob)
            self.checkJobs()

        currentTorrentJob = next(filter(lambda e: e.jobType == "torrent", self.currentJobs), None)
        if currentTorrentJob == None:
            availableTorrentJob = next(filter(lambda e: e.jobType == "torrent", self.jobs), None)
            if availableTorrentJob != None:
                self.jobs.remove(availableTorrentJob)
                self.currentJobs.append(availableTorrentJob)
                availableTorrentJob.start()
        elif currentTorrentJob.is_alive() == False:
            self.completedJobs.append(currentTorrentJob)
            self.currentJobs.remove(currentTorrentJob)
            self.checkJobs()

        currentUploadJob = next(filter(lambda e: e.jobType == "upload", self.currentJobs), None)
        if currentUploadJob == None:
            availableUploadJob = next(filter(lambda e: e.jobType == "upload", self.jobs), None)
            if availableUploadJob != None:
                self.jobs.remove(availableUploadJob)
                self.currentJobs.append(availableUploadJob)
                availableUploadJob.start()
        elif currentUploadJob.is_alive() == False:
            self.completedJobs.append(currentUploadJob)
            self.currentJobs.remove(currentUploadJob)
            self.checkJobs()

    def run(self):
        setInterval(1, self.asyncRun)
        system("mkdir -p /usr/src/nyananime/src-episodes")
        system("mkdir -p /usr/src/nyananime/dest-episodes")

        while 1:
            printMainUI(self)

dashboard = Dashboard()