import subprocess, os
from os import system, path
from job.job import Job

class DownloadJob(Job):
    def __init__(self, dashboard, jobShowID, jobEpisodeIndex, jobMagnet):
        Job.__init__(self, dashboard, "download")
        self.jobShowID = jobShowID
        self.jobEpisodeIndex = jobEpisodeIndex
        self.jobMagnet = jobMagnet
        self.jobPath = f"{self.jobShowID}/{self.jobEpisodeIndex}" if self.jobEpisodeIndex != None else self.jobShowID
        self.jobName = f"Download job for '{self.jobPath}'"

    def run(self):
        DEVNULL = open(os.devnull, 'wb')

        self.startSection(f"Downloading files for '{self.jobPath}'...")
        system(f"mkdir -p {self.dashboard.fileSystem.basePath}/torrents/{self.jobPath}")
        if self.jobEpisodeIndex != None: system(f'mkdir -p {self.dashboard.fileSystem.basePath}/source/{self.jobShowID}')
        if not path.exists(f"{self.dashboard.fileSystem.basePath}/source/{self.jobPath}"):
            system(f'ln -sf {self.dashboard.fileSystem.basePath}/torrents/{self.jobPath} {self.dashboard.fileSystem.basePath}/source/{self.jobPath}')

        system(f"echo '{self.jobMagnet}' > {self.dashboard.fileSystem.basePath}/torrents/{self.jobPath}/link.conf")
        self.jobSubprocess = subprocess.Popen(["transmission-cli", "-v", "-w", f"{self.dashboard.fileSystem.basePath}/torrents/{self.jobPath}", self.jobMagnet], stdin=DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
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
        
        self.jobName = f"Download job for '{self.jobPath}'"
        DEVNULL.close()