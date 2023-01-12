import subprocess, os
from job.job import Job

class UploadJob(Job):
    def __init__(self, dashboard, jobShowID, jobEpisodeIndex):
        Job.__init__(self, dashboard, "upload")
        self.jobShowID = jobShowID
        self.jobEpisodeIndex = jobEpisodeIndex
        self.jobPath = f"{self.jobShowID}/{self.jobEpisodeIndex}" if self.jobEpisodeIndex != None else self.jobShowID
        self.jobName = f"Upload job for '{self.jobPath}'"

    def run(self):
        DEVNULL = open(os.devnull, 'wb')
        
        self.startSection(f"Uploading image files for '{self.jobPath}'...")
        self.jobSubprocess = subprocess.Popen(["rsync", "-am", "--info=progress2", "--include=*/", "--include=*.webp", "--include=*.jpg", "--exclude=*", "-e", f"ssh -o StrictHostKeyChecking=no -i {self.dashboard.fileSystem.basePath}/ssh/id_rsa", f"{self.dashboard.fileSystem.basePath}/processed/{self.jobPath}/", f"{os.environ['COMFY_IMAGE_USER']}@{os.environ['COMFY_IMAGE_HOST']}:{os.environ['COMFY_IMAGE_PATH']}/{self.jobPath}/"], stdin=DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        while self.jobSubprocess.stdout != None:
            line = str(self.jobSubprocess.stdout.readline())
            if not line: break
            if "%" in line:
                self.jobProgress = int(line[line.index("%")-3:line.index("%")])
                self.jobDetails = line[line.index("%")+1:line.index("/s")+2].strip()
        self.jobSubprocess.wait()
        self.endSection()
        
        self.startSection(f"Uploading video files for '{self.jobPath}'...")
        self.jobSubprocess = subprocess.Popen(["rsync", "-am", "--info=progress2", "--include=*/", "--exclude=*.webp", "--exclude=*.jpg", "-e", f"ssh -o StrictHostKeyChecking=no -i {self.dashboard.fileSystem.basePath}/ssh/id_rsa", f"{self.dashboard.fileSystem.basePath}/processed/{self.jobPath}/", f"{os.environ['COMFY_VIDEO_USER']}@{os.environ['COMFY_VIDEO_HOST']}:{os.environ['COMFY_VIDEO_PATH']}/{self.jobPath}/"], stdin=DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        while self.jobSubprocess.stdout != None:
            line = str(self.jobSubprocess.stdout.readline())
            if not line: break
            if "%" in line:
                self.jobProgress = int(line[line.index("%")-3:line.index("%")])
                self.jobDetails = line[line.index("%")+1:line.index("/s")+2].strip()
        self.jobSubprocess.wait()
        self.endSection()
        
        self.jobName = f"Upload job for '{self.jobPath}'"
        DEVNULL.close()