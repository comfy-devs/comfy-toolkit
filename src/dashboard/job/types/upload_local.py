import os
from job.job import Job
import shutil

class UploadLocalJob(Job):
    def __init__(self, dashboard, jobShowID, jobEpisodeIndex, jobMove=False):
        Job.__init__(self, dashboard, "move")
        self.jobShowID = jobShowID
        self.jobEpisodeIndex = jobEpisodeIndex
        self.jobPath = f"{self.jobShowID}/{self.jobEpisodeIndex}" if self.jobEpisodeIndex != None else self.jobShowID
        self.jobName = f"Upload local job for '{self.jobPath}'"
        self.jobMove = jobMove

    def run(self):
        jobDir = f"{self.dashboard.fileSystem.basePath}/processed/{self.jobPath}"
        methodText = "Moving" if self.jobMove else "Copying"
        self.startSection(f"{methodText} files for '{self.jobPath}'...")
        for root, _, files in os.walk(jobDir):
            for name in files:
                if name.endswith(".jpg") or name.endswith(".webp"):
                    path = f"/usr/src/data/image/{self.jobPath}/{os.path.relpath(root, jobDir)}/{name}"
                elif not name == "episode_x264.mp4" and not name == "episode_vp9.webm":
                    path = f"/usr/src/data/video/{self.jobPath}/{os.path.relpath(root, jobDir)}/{name}"
                else:
                    continue
                if os.path.exists(path):
                    continue
                os.makedirs(os.path.dirname(path), exist_ok=True)
                try:
                    if self.jobMove:
                        shutil.move(f"{root}/{name}", path)
                    else:
                        shutil.copy(f"{root}/{name}", path)
                except:
                    print(f"failed to process {path}")
        self.endSection()
        
        self.jobName = f"Upload local job for '{self.jobPath}'"