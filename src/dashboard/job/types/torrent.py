import subprocess, os
from job.job import Job

class TorrentJob(Job):
    def __init__(self, jobAnimeID):
        Job.__init__(self, "torrent")
        self.jobName = f"Torrent job for '{jobAnimeID}'"
        self.jobAnimeID = jobAnimeID

    def run(self):
        DEVNULL = open(os.devnull, 'wb')
        
        self.startSection(f"Creating torrent for '{self.jobAnimeID}'")
        self.jobSubprocess = subprocess.Popen(["../scripts/torrent-create.sh", f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}", f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/series.torrent", self.jobAnimeID, "Auto-generated torrent for Nyan Anime."], stdin=DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while self.jobSubprocess.stdout != None:
            line = str(self.jobSubprocess.stdout.readline())
            if not line: break
            self.jobProgress = float(line)
        self.jobSubprocess.wait()
        self.endSection()
        
        self.jobName = f"Torrent job for '{self.jobAnimeID}'"
        DEVNULL.close()