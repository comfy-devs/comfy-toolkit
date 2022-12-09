import subprocess, os
from job.job import Job
from job.types.transcoding import TranscodingJob

class TranscodingCreateJob(Job):
    def __init__(self, dashboard, jobAnimeID, jobEpisodeIndex, jobStartIndex, jobCollection):
        Job.__init__(self, dashboard, "transcoding-create")
        self.jobAnimeID = jobAnimeID
        self.jobEpisodeIndex = jobEpisodeIndex
        self.jobStartIndex = jobStartIndex
        self.jobCollection = jobCollection
        self.jobPath = f"{self.jobAnimeID}/{self.jobEpisodeIndex}" if self.jobEpisodeIndex != None else self.jobAnimeID
        self.jobName = f"Transcoding create job for '{self.jobPath}'"

    def run(self):
        DEVNULL = open(os.devnull, 'wb')

        jobs = []
        entries = subprocess.getoutput(f'find {self.dashboard.fileSystem.basePath}/source/{self.jobPath}/ -type f -name "*.mkv" -printf "%P\\n" | sort').split("\n")
        i = self.jobStartIndex
        for entry in entries:
            jobs.append(TranscodingJob(self.dashboard, self.jobAnimeID, i, f"source/{self.jobPath}/{entry}", "x264", []))
            i += 1
        jobs.extend(self.jobCollection.jobs)
        self.jobCollection.jobs = jobs
        
        self.jobName = f"Transcoding create job for '{self.jobPath}'"
        DEVNULL.close()