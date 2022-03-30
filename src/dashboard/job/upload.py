import subprocess, os
from os import system, path
from util.general import colorize
from job.job import Job

class UploadJob(Job):
    def __init__(self, jobAnimeID, jobEpisodeIndex):
        Job.__init__(self, "upload")
        self.jobAnimeID = jobAnimeID
        self.jobEpisodeIndex = jobEpisodeIndex
        self.jobPath = f"{self.jobAnimeID}/{self.jobEpisodeIndex}" if self.jobEpisodeIndex != None else self.jobAnimeID
        self.jobName = f"Upload job for '{self.jobPath}'"

    def run(self):
        DEVNULL = open(os.devnull, 'wb')
        
        self.startSection(f"Uploading image files for '{self.jobPath}'...")
        self.jobSubprocess = subprocess.Popen(["rsync", "-am", "--info=progress2", "--include=*/", "--include=*.webp", "--include=*.jpg", "--exclude=*", "-e", "ssh -o StrictHostKeyChecking=no -i /usr/src/nyananime/ssh/id_rsa", f"/usr/src/nyananime/dest-episodes/{self.jobPath}/", f"{os.environ['NYANANIME_IMAGE_USER']}@{os.environ['NYANANIME_IMAGE_HOST']}:{os.environ['NYANANIME_IMAGE_PATH']}/{self.jobPath}/"], stdin=DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines='\r')
        while True:
            line = self.jobSubprocess.stdout.readline()
            if not line: break
            if "%" in line:
                self.jobProgress = int(line[line.index("%")-3:line.index("%")])
                self.jobSpeed = line[line.index("%")+1:line.index("/s")+2].strip()
        self.jobSubprocess.wait()
        self.endSection()
        
        self.startSection(f"Uploading video files for '{self.jobPath}'...")
        self.jobSubprocess = subprocess.Popen(["rsync", "-am", "--info=progress2", "--include=*/", "--exclude=*.webp", "--exclude=*.jpg", "-e", "ssh -o StrictHostKeyChecking=no -i /usr/src/nyananime/ssh/id_rsa", f"/usr/src/nyananime/dest-episodes/{self.jobPath}/", f"{os.environ['NYANANIME_VIDEO_USER']}@{os.environ['NYANANIME_VIDEO_HOST']}:{os.environ['NYANANIME_VIDEO_PATH']}/{self.jobPath}/"], stdin=DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines='\r')
        while True:
            line = self.jobSubprocess.stdout.readline()
            if not line: break
            if "%" in line:
                self.jobProgress = int(line[line.index("%")-3:line.index("%")])
                self.jobSpeed = line[line.index("%")+1:line.index("/s")+2].strip()
        self.jobSubprocess.wait()
        self.endSection()
        
        self.jobName = f"Upload job for '{self.jobPath}'"
        DEVNULL.close()