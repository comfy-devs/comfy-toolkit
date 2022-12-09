import subprocess, os
from job.job import Job

class TorrentJob(Job):
    def __init__(self, dashboard, jobAnimeID):
        Job.__init__(self, dashboard, "torrent")
        self.jobAnimeID = jobAnimeID
        self.jobPath = self.jobAnimeID
        self.jobName = f"Torrent job for '{self.jobPath}'"

    def run(self):
        DEVNULL = open(os.devnull, 'wb')
        
        self.startSection(f"Creating torrent for '{self.jobPath}'")
        self.jobSubprocess = subprocess.Popen(["../scripts/torrent-create.sh", f"{self.dashboard.fileSystem.basePath}/processed/{self.jobPath}", f"{self.dashboard.fileSystem.basePath}/processed/{self.jobPath}/series.torrent", self.jobAnimeID, "Auto-generated torrent for Nyan Anime."], stdin=DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while self.jobSubprocess.stdout != None:
            line = str(self.jobSubprocess.stdout.readline())
            if not line: break
            self.jobProgress = float(line)
        self.jobSubprocess.wait()
        self.endSection()
        
        self.jobName = f"Torrent job for '{self.jobPath}'"
        DEVNULL.close()