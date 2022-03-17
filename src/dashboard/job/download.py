import subprocess, os
from os import system, path
from util.general import colorize
from job.job import Job

class DownloadJob(Job):
    def __init__(self, jobAnimeID, jobMagnet):
        Job.__init__(self, "download")
        self.jobAnimeID = jobAnimeID
        self.jobMagnet = jobMagnet
        self.jobName = f"Download job for '{self.jobAnimeID}'"

    def run(self):
        DEVNULL = open(os.devnull, 'wb')
        
        self.startSection(f"Downloading files for '{self.jobAnimeID}'...")
        system(f"mkdir -p /usr/src/nyananime/torrents/{self.jobAnimeID}")
        system(f"echo '{self.jobMagnet}' > /usr/src/nyananime/torrents/{self.jobAnimeID}/series.txt")
        self.jobSubprocess = subprocess.Popen(["transmission-cli", "-w", f"/usr/src/nyananime/torrents/{self.jobAnimeID}", self.jobMagnet], stdin=DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines='\r')
        while True:
            line = self.jobSubprocess.stdout.readline()
            if not line: break
            if ": " in line:
                self.jobProgress = float(line[line.index(": ")+2:line.index("%")])
                self.jobSpeed = line[line.index("(")+1:line.index(")")]
                if self.jobProgress == 100.0:
                    self.jobSubprocess.kill()
        self.jobSubprocess.wait()
        self.endSection()
        
        self.jobName = f"Download job for '{self.jobAnimeID}'"
        DEVNULL.close()