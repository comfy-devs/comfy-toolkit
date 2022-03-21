import subprocess, os
from os import system, path
from util.general import colorize
from job.job import Job
from job.transcoding import TranscodingJob

class TranscodingCreateJob(Job):
    def __init__(self, jobAnimeID, jobStartIndex, jobCollection):
        Job.__init__(self, "transcodingCreate")
        self.jobAnimeID = jobAnimeID
        self.jobStartIndex = jobStartIndex
        self.jobCollection = jobCollection
        self.jobName = f"Transcoding create job for '{self.jobAnimeID}'"

    def run(self):
        DEVNULL = open(os.devnull, 'wb')

        jobs = []
        entries = subprocess.getoutput(f'find /usr/src/nyananime/src-episodes/{self.jobAnimeID}/ -type f -name "*.mkv" -printf "%P\\n" | sort').split("\n")
        i = 0
        for entry in entries:
            jobs.append(TranscodingJob(self.jobAnimeID, self.jobStartIndex + i, entry, "x264", []))
            i += 1
        jobs.extend(self.jobCollection.jobs)
        self.jobCollection.jobs = jobs
        
        self.jobName = f"Transcoding create job for '{self.jobAnimeID}'"
        DEVNULL.close()