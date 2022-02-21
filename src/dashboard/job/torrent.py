import subprocess, os
from os import system, path
from util.general import colorize
from job.job import Job

class TorrentJob(Job):
    def setup(self, jobAnimeID):
        self.jobName = f"Creating torrent for '{jobAnimeID}'..."
        self.jobAnimeID = jobAnimeID

    def run(self):
        self.jobStatus = "working"
        DEVNULL = open(os.devnull, 'wb')
        
        self.jobSubprocess = subprocess.Popen(["../scripts/torrent-create.sh", f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}", f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/series.torrent", self.jobAnimeID, "Auto-generated torrent for Nyan Anime."], stdin=DEVNULL, stdout=subprocess.PIPE, stderr=DEVNULL)
        while True:
            line = self.jobSubprocess.stdout.readline()
            if not line: break
            self.jobProgress = float(line)
        self.jobSubprocess.wait()
        
        self.jobName = f"Torrent job for '{self.jobAnimeID}'"
        self.jobStatus = "finished"
        DEVNULL.close()