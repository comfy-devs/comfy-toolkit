import subprocess, os
from job.job import Job

class TorrentJob(Job):
    def __init__(self, dashboard, jobShowID):
        Job.__init__(self, dashboard, "torrent")
        self.jobShowID = jobShowID
        self.jobPath = self.jobShowID
        self.jobName = f"Torrent job for '{self.jobPath}'"

    def run(self):
        DEVNULL = open(os.devnull, 'wb')
        
        self.startSection(f"Creating torrent for '{self.jobPath}'")
        self.jobSubprocess = subprocess.Popen(["../scripts/torrent-create.sh", f"{self.dashboard.fileSystem.basePath}/processed/{self.jobPath}", f"{self.dashboard.fileSystem.basePath}/misc/{self.jobPath}", self.jobShowID, "Auto-generated torrent for Comfy."], stdin=DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while self.jobSubprocess.stdout != None:
            line = str(self.jobSubprocess.stdout.readline())
            if not line: break
            self.jobProgress = round(float(line[line.index("progress=")+len("progress="):line.index("\\n")].strip()), 2)
        self.jobSubprocess.wait()
        self.endSection()
        
        self.jobName = f"Torrent job for '{self.jobPath}'"
        DEVNULL.close()