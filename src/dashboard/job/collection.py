class JobCollection():
    def __init__(self, name, jobs):
        self.name = name
        self.status = "working"
        self.jobs = jobs
        self.currentJob = None
        self.completedJobs = []
        self.onComplete = None