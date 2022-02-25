import subprocess, os
from os import system, path
from util.general import colorize
from job.job import Job

class UploadJob(Job):
    def setup(self, jobAnimeID):
        self.jobAnimeID = jobAnimeID
        self.jobName = f"Upload job for '{self.jobAnimeID}'"

    def run(self):
        DEVNULL = open(os.devnull, 'wb')
        
        self.startSection(f"Uploading image files for '{self.jobAnimeID}'...")
        self.jobSubprocess = subprocess.Popen(["rsync", "-am", "--info=progress2", "--include=*/", "--include=*.webp", "--include=*.jpg", "--exclude=*", "-e", "ssh -o StrictHostKeyChecking=no -i /usr/src/nyananime/ssh/id_rsa", f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/", f"{os.environ['NYANANIME_IMAGE_USER']}@{os.environ['NYANANIME_IMAGE_HOST']}:{os.environ['NYANANIME_IMAGE_PATH']}/{self.jobAnimeID}/"], stdin=DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines='\r')
        while True:
            line = self.jobSubprocess.stdout.readline()
            if not line: break
            if "%" in line:
                self.jobProgress = int(line[line.index("%")-3:line.index("%")])
                self.jobSpeed = line[line.index("%")+1:line.index("/s")+2].strip()
        self.jobSubprocess.wait()
        self.endSection()
        
        self.startSection(f"Uploading video files for '{self.jobAnimeID}'...")
        self.jobSubprocess = subprocess.Popen(["rsync", "-am", "--info=progress2", "--include=*/", "--exclude=*.webp", "--exclude=*.jpg", "-e", "ssh -o StrictHostKeyChecking=no -i /usr/src/nyananime/ssh/id_rsa", f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/", f"{os.environ['NYANANIME_VIDEO_USER']}@{os.environ['NYANANIME_VIDEO_HOST']}:{os.environ['NYANANIME_VIDEO_PATH']}/{self.jobAnimeID}/"], stdin=DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines='\r')
        while True:
            line = self.jobSubprocess.stdout.readline()
            if not line: break
            if "%" in line:
                self.jobProgress = int(line[line.index("%")-3:line.index("%")])
                self.jobSpeed = line[line.index("%")+1:line.index("/s")+2].strip()
        self.jobSubprocess.wait()
        self.endSection()
        
        self.jobName = f"Upload job for '{self.jobAnimeID}'"
        DEVNULL.close()