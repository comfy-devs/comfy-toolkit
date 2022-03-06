class JobCollection():
    def __init__(self, name, jobs):
        self.name = name
        self.jobs = jobs
        self.currentJob = None
        self.completedJobs = []