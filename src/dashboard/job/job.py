import threading, subprocess, os
from os import system, path
from util.general import colorize

# ffprobe -v error -select_streams s -show_entries stream=index -of csv=p=0 "[Erai-raws] Yuru Camp - 01 ~ 12 [1080p][Multiple Subtitle]/[Erai-raws] Yuru Camp - 01 [1080p][Multiple Subtitle].mkv" | wc -w
# ffprobe -v error -select_streams s:1 -show_entries stream=index:stream_tags=language -of csv=p=0 "[Erai-raws] Yuru Camp - 01 ~ 12 [1080p][Multiple Subtitle]/[Erai-raws] Yuru Camp - 01 [1080p][Multiple Subtitle].mkv"

class Job(threading.Thread):
    def __init__(self, jobType, jobName):
        threading.Thread.__init__(self)
        self.jobType = jobType
        self.jobName = jobName
        self.jobStatus = "waiting"
        self.jobProgress = 0
        self.jobLogs = []
        self.jobSubprocess = None

    def setupTranscoding(self, jobAnimeID, jobEpisodeIndex, jobSrcFile, jobCodec, jobVideoOptions):
        self.jobAnimeID = jobAnimeID
        self.jobEpisodeIndex = jobEpisodeIndex
        self.jobSrcFile = jobSrcFile
        self.jobCodec = jobCodec
        self.jobVideoOptions = jobVideoOptions

    def run(self):
        self.jobStatus = "working"
        DEVNULL = open(os.devnull, 'wb')

        system(f'mkdir -p "/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}"')
        audioStreams = subprocess.getoutput(f'ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "/usr/src/nyananime/src-episodes/{self.jobAnimeID}/{self.jobSrcFile}" | wc -w')
        if self.jobCodec == "x264":
            system(f'mkdir -p "/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/hls/x264"')
            if not path.exists(f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/hls/x264/master.m3u8"):
                if not path.exists(f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/episode_x264.mp4"):
                    self.jobLogs.append(f'Transcoding x264 video...')
                    args = [f"../scripts/ffmpeg-video-x264-medium.sh", f"/usr/src/nyananime/src-episodes/{self.jobAnimeID}/{self.jobSrcFile}", f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}"]
                    self.jobSubprocess = subprocess.Popen(args, stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
                    self.jobSubprocess.wait()
                else:
                    self.jobLogs.append(f'x264 video already transcoded. Skipping...')
                
                self.jobLogs.append(f'Generating x264 HLS streams...')
                script = "../scripts/ffmpeg-video-x264-hls.sh" if int(audioStreams) <= 1 else "../scripts/ffmpeg-video-x264-hls-dub.sh"
                args = [script, f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/episode_x264.mp4", f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}"]
                self.jobSubprocess = subprocess.Popen(args, stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
                self.jobSubprocess.wait()
                # system(f'rm "/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/episode_x264.mp4"')
            else:
                self.jobLogs.append(f'x264 HLS streams already generated. Skipping...')
        elif self.jobCodec == "vp9":
            system(f'mkdir -p "/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/hls/vp9"')
            if not path.exists(f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/hls/vp9/master.m3u8"):
                if not path.exists(f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/episode_vp9.webm"):
                    self.jobLogs.append(f'Transcoding VP9 video...')
                    args = [f"../scripts/ffmpeg-video-vp9.sh", f"/usr/src/nyananime/src-episodes/{self.jobAnimeID}/{self.jobSrcFile}", f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}"]
                    args.extend(self.jobVideoOptions)
                    self.jobSubprocess = subprocess.Popen(args, stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
                    self.jobSubprocess.wait()
                else:
                    self.jobLogs.append(f'VP9 video already transcoded. Skipping...')
                
                self.jobLogs.append(f'Generating VP9 HLS streams...')
                script = "../scripts/ffmpeg-video-vp9-hls.sh" if int(audioStreams) <= 1 else "../scripts/ffmpeg-video-vp9-hls-dub.sh"
                args = [script, f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/episode_vp9.webm", f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}"]
                self.jobSubprocess = subprocess.Popen(args, stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
                self.jobSubprocess.wait()
                # system(f'rm "/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/episode_vp9.webm"')
            else:
                self.jobLogs.append(f'VP9 HLS streams already generated. Skipping...')

        system(f'mkdir -p "/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/subs"')
        subtitleStreams = subprocess.getoutput(f'ffprobe -v error -select_streams s -show_entries stream=index -of csv=p=0 "/usr/src/nyananime/src-episodes/{self.jobAnimeID}/{self.jobSrcFile}" | wc -w')
        for i in range(int(subtitleStreams)):
            subtitleStreamLanguage = subprocess.getoutput(f'ffprobe -v error -select_streams s:{i} -show_entries stream=index:stream_tags=language -of csv=p=0 "/usr/src/nyananime/src-episodes/{self.jobAnimeID}/{self.jobSrcFile}"')
            subtitleStreamLanguage = subtitleStreamLanguage[(subtitleStreamLanguage.index(",") + 1):]
            if not path.exists(f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/subs/{subtitleStreamLanguage}.vtt"):
                self.jobLogs.append(f'Extracting \'{colorize("gray", subtitleStreamLanguage)}\' subtitles...')
                self.jobSubprocess = subprocess.Popen(["../scripts/ffmpeg-subs.sh", f"/usr/src/nyananime/src-episodes/{self.jobAnimeID}/{self.jobSrcFile}", f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/subs/{subtitleStreamLanguage}.vtt", f"{i}"], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
                self.jobSubprocess.wait()
                self.jobSubprocess = subprocess.Popen(["../scripts/subs-clean.sh", f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/subs/{subtitleStreamLanguage}.vtt"], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
                self.jobSubprocess.wait()
                self.jobSubprocess = subprocess.Popen(["../scripts/subs-clean-ad.sh", f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/subs/{subtitleStreamLanguage}.vtt"], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
                self.jobSubprocess.wait()
            else:
                self.jobLogs.append(f'\'{colorize("gray", subtitleStreamLanguage)}\' subtitles already extracted. Skipping...')

        if not path.exists(f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/thumbnail.webp"):
            self.jobLogs.append(f'Generating thumbnail...')
            self.jobSubprocess = subprocess.Popen(["../scripts/ffmpeg-thumbnail.sh", f"/usr/src/nyananime/src-episodes/{self.jobAnimeID}/{self.jobSrcFile}", f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}"], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
            self.jobSubprocess.wait()
        else:
            self.jobLogs.append(f'Thumbnail already generated. Skipping...')

        if not path.exists(f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/chapters.json"):
            self.jobLogs.append(f'Extracting chapters...')
            self.jobSubprocess = subprocess.Popen(["../scripts/ffmpeg-chapters.sh", f"/usr/src/nyananime/src-episodes/{self.jobAnimeID}/{self.jobSrcFile}", f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}"], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
            self.jobSubprocess.wait()
        else:
            self.jobLogs.append(f'Chapters already extracted. Skipping...')

        if not path.exists(f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/stats.json"):
            self.jobLogs.append(f'Generating stats...')
            self.jobSubprocess = subprocess.Popen(["../scripts/ffmpeg-stats.sh", f"/usr/src/nyananime/src-episodes/{self.jobAnimeID}/{self.jobSrcFile}", f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}"], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
            self.jobSubprocess.wait()
        else:
            self.jobLogs.append(f'Stats already generated. Skipping...')
        
        self.jobStatus = "finished"
        DEVNULL.close()