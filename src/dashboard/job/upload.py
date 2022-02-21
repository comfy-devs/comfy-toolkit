import subprocess, os
from os import system, path
from util.general import colorize
from job.job import Job

class UploadJob(Job):
    def setup(self, jobAnimeID):
        self.jobName = f"Uploading image files for '{jobAnimeID}'..."
        self.jobAnimeID = jobAnimeID

    def run(self):
        self.jobStatus = "working"
        DEVNULL = open(os.devnull, 'wb')
        
        self.jobSubprocess = subprocess.Popen(["rsync", "-am", "--info=progress2", "--include=*/", "--include=*.webp", "--exclude=*", "-e", "ssh -i /usr/src/nyananime/ssh/rsa_id", f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/", f"{os.environ['NYANANIME_IMAGE_USER']}@{os.environ['NYANANIME_IMAGE_HOST']}:{os.environ['NYANANIME_IMAGE_PATH']}/{self.jobAnimeID}/"], stdin=DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines='\r')
        while True:
            line = self.jobSubprocess.stdout.readline()
            if not line: break
        self.jobSubprocess.wait()
        
        self.jobName = f"Uploading video files for '{self.jobAnimeID}'..."
        self.jobSubprocess = subprocess.Popen(["rsync", "-am", "--info=progress2", "--include=*/", "--exclude=*.webp", "-e", "ssh -i /usr/src/nyananime/ssh/rsa_id", f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/", f"{os.environ['NYANANIME_VIDEO_USER']}@{os.environ['NYANANIME_VIDEO_HOST']}:{os.environ['NYANANIME_VIDEO_PATH']}/{self.jobAnimeID}/"], stdin=DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines='\r')
        while True:
            line = self.jobSubprocess.stdout.readline()
            if not line: break
            if "%" in line:
                self.jobProgress = int(line[line.index("%")-3:line.index("%")])
        self.jobSubprocess.wait()
        
        self.jobName = f"Upload job for '{self.jobAnimeID}'"
        self.jobStatus = "finished"
        DEVNULL.close()