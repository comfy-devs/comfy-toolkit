import subprocess, os
from os import system, path
from job.job import Job

class DownloadJob(Job):
    def __init__(self, jobAnimeID, jobEpisodeIndex, jobMagnet):
        Job.__init__(self, "download")
        self.jobAnimeID = jobAnimeID
        self.jobEpisodeIndex = jobEpisodeIndex
        self.jobMagnet = jobMagnet
        self.jobPath = f"/{self.jobEpisodeIndex}" if self.jobEpisodeIndex != None else ""
        self.jobName = f"Download job for '{self.jobAnimeID}{self.jobPath}'"

    def run(self):
        DEVNULL = open(os.devnull, 'wb')

        self.startSection(f"Downloading files for '{self.jobAnimeID}{self.jobPath}'...")
        system(f"mkdir -p /usr/src/nyananime/torrents/{self.jobAnimeID}{self.jobPath}")
        if self.jobEpisodeIndex != None: system(f'mkdir -p /usr/src/nyananime/src-episodes/{self.jobAnimeID}')
        if not path.exists(f"/usr/src/nyananime/src-episodes/{self.jobAnimeID}{self.jobPath}"):
            system(f'ln -sf /usr/src/nyananime/torrents/{self.jobAnimeID}{self.jobPath} /usr/src/nyananime/src-episodes/{self.jobAnimeID}{self.jobPath}')

        system(f"echo '{self.jobMagnet}' > /usr/src/nyananime/torrents/{self.jobAnimeID}{self.jobPath}/link.conf")
        self.jobSubprocess = subprocess.Popen(["transmission-cli", "-v", "-w", f"/usr/src/nyananime/torrents/{self.jobAnimeID}{self.jobPath}", self.jobMagnet], stdin=DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        while self.jobSubprocess.stdout != None:
            line = str(self.jobSubprocess.stdout.readline())
            if not line: break
            if ": " in line:
                self.jobProgress = float(line[line.index(": ")+2:line.index("%")])
                self.jobDetails = line[line.index("(")+1:line.index(")")]
            elif "Seeding" in line:
                self.jobSubprocess.kill()
        self.jobSubprocess.wait()
        self.endSection()
        
        self.jobName = f"Download job for '{self.jobAnimeID}{self.jobPath}'"
        DEVNULL.close()