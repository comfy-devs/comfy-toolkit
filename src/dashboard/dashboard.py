from os import system
from util.general import setInterval, colorize
from ui.main import printMainUI
from ui.jobs import printJobsUI

class Dashboard:
    def __init__(self):
        self.jobs = []
        self.currentJob = None
        self.completedJobs = []
        self.jobsUIEnabled = False
        self.jobsUIShowCompleted = True
        self.run()
        
    def asyncRun(self):
        if self.jobsUIEnabled == True:
            printJobsUI(self)
        
        if self.currentJob != None and self.currentJob.is_alive() == False:
            self.completedJobs.append(self.currentJob)
            self.currentJob = None
        
        if self.currentJob == None and len(self.jobs) > 0:
            self.currentJob = self.jobs.pop(0)
            self.currentJob.start()

    def run(self):
        setInterval(1, self.asyncRun)
        system("mkdir -p /usr/src/nyananime/src-episodes")
        system("mkdir -p /usr/src/nyananime/dest-episodes")

        while 1:
            printMainUI(self)

dashboard = Dashboard()