import threading, subprocess, os
from os import system, path
from util import getColor

class Job(threading.Thread):
    def __init__(self, jobType, jobName):
        threading.Thread.__init__(self)
        self.jobType = jobType
        self.jobName = jobName
        self.jobStatus = "waiting"
        self.jobProgress = 0
        self.jobLogs = []
        self.jobSubprocess = None

    def setupTranscoding(self, jobAnimeID, jobEpisodeIndex, jobSrcFile, jobDestFile, jobVideoScript, jobVideoOptions):
        self.jobAnimeID = jobAnimeID
        self.jobEpisodeIndex = jobEpisodeIndex
        self.jobSrcFile = jobSrcFile
        self.jobDestFile = jobDestFile
        self.jobVideoScript = jobVideoScript
        self.jobVideoOptions = jobVideoOptions

    def run(self):
        self.jobStatus = "working"
        DEVNULL = open(os.devnull, 'wb')

        system(f'mkdir -p "/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}"')
        if not path.exists(f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/{self.jobDestFile}"):
            self.jobLogs.append(f'Transcoding episode {getColor("gray")}\'{self.jobSrcFile}\'{getColor("reset")}...')
            args = [f"../scripts/{self.jobVideoScript}", f"/usr/src/nyananime/src-episodes/{self.jobAnimeID}/{self.jobSrcFile}", f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}"]
            args.extend(self.jobVideoOptions)
            self.jobSubprocess = subprocess.Popen(args, stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
            self.jobSubprocess.wait()
        else:
            self.jobLogs.append(f'Transcoding of {getColor("gray")}\'{self.jobSrcFile}\'{getColor("reset")} already done. Skipping...')

        if not path.exists(f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/subs_en.vtt"):
            self.jobLogs.append(f'Generating subtitles for {getColor("gray")}\'{self.jobSrcFile}\'{getColor("reset")}...')
            self.jobSubprocess = subprocess.Popen(["../scripts/ffmpeg-subs.sh", f"/usr/src/nyananime/src-episodes/{self.jobAnimeID}/{self.jobSrcFile}", f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}"], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
            self.jobSubprocess.wait()
            self.jobSubprocess = subprocess.Popen(["../scripts/ffmpeg-subs-clean.sh", f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}"], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
            self.jobSubprocess.wait()
            self.jobSubprocess = subprocess.Popen(["../scripts/ffmpeg-subs-clean-ad.sh", f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}"], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
            self.jobSubprocess.wait()
        else:
            self.jobLogs.append(f'Subtitles for {getColor("gray")}\'{self.jobSrcFile}\'{getColor("reset")} already done. Skipping...')

        if not path.exists(f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/thumbnail.webp"):
            self.jobLogs.append(f'Generating thumbnail for {getColor("gray")}\'{self.jobSrcFile}\'{getColor("reset")}...')
            self.jobSubprocess = subprocess.Popen(["../scripts/ffmpeg-thumbnail.sh", f"/usr/src/nyananime/src-episodes/{self.jobAnimeID}/{self.jobSrcFile}", f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}"], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
            self.jobSubprocess.wait()
        else:
            self.jobLogs.append(f'Thumbnail for {getColor("gray")}\'{self.jobSrcFile}\'{getColor("reset")} already done. Skipping...')

        if not path.exists(f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/chapters.json"):
            self.jobLogs.append(f'Generating chapters for {getColor("gray")}\'{self.jobSrcFile}\'{getColor("reset")}...')
            self.jobSubprocess = subprocess.Popen(["../scripts/ffmpeg-chapters.sh", f"/usr/src/nyananime/src-episodes/{self.jobAnimeID}/{self.jobSrcFile}", f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}"], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
            self.jobSubprocess.wait()
        else:
            self.jobLogs.append(f'Chapters for {getColor("gray")}\'{self.jobSrcFile}\'{self.jobSrcFile} already done. Skipping...')

        if not path.exists(f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/stats.json"):
            self.jobLogs.append(f'Generating stats for {getColor("gray")}\'{self.jobSrcFile}\'{getColor("reset")}...')
            self.jobSubprocess = subprocess.Popen(["../scripts/ffmpeg-stats.sh", f"/usr/src/nyananime/src-episodes/{self.jobAnimeID}/{self.jobSrcFile}", f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}"], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
            self.jobSubprocess.wait()
        else:
            self.jobLogs.append(f'Stats for {getColor("gray")}\'{self.jobSrcFile}\'{getColor("reset")} already done. Skipping...')
        
        self.jobStatus = "finished"
        DEVNULL.close()