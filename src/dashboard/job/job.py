import threading
from util.general import colorize

class Job(threading.Thread):
    def __init__(self, jobType):
        threading.Thread.__init__(self)
        self.jobType = jobType
        self.jobName = "??"
        self.jobStatus = "waiting"
        self.jobProgress = 0
        self.jobSubprocess = None