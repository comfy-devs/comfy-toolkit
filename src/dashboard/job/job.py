import threading

class Job(threading.Thread):
    def __init__(self, jobType):
        threading.Thread.__init__(self)
        self.jobType = jobType
        self.jobName = "??"
        self.jobProgress = 0
        self.jobSpeed = "--"
        self.jobSubprocess = None

    def startSection(self, name):
        self.jobName = name
        self.jobProgress = 0
        self.jobSpeed = "??"

    def endSection(self):
        self.jobProgress = 100
        self.jobSpeed = "--"