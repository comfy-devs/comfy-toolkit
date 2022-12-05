import threading

class Job(threading.Thread):
    def __init__(self, jobType):
        threading.Thread.__init__(self)
        self.jobType = jobType
        self.jobName = "??"
        self.jobProgress = 0
        self.jobDetails = "--"
        self.jobSubprocess = None
        self.jobOnComplete = None

    def startSection(self, name):
        self.jobName = name
        self.jobProgress = 0
        self.jobDetails = "??"

    def endSection(self):
        self.jobProgress = 100
        self.jobDetails = "--"