import subprocess, os
from os import system, path
from util.general import colorize
from job.job import Job

class TranscodingJob(Job):
    def setup(self, jobAnimeID, jobEpisodeIndex, jobSrcFile, jobCodec, jobVideoOptions):
        self.jobName = f"Transcoding '{jobSrcFile}' ({jobCodec})..."
        self.jobAnimeID = jobAnimeID
        self.jobEpisodeIndex = jobEpisodeIndex
        self.jobSrcFile = jobSrcFile
        self.jobCodec = jobCodec
        self.jobVideoOptions = jobVideoOptions

    def run(self):
        self.jobStatus = "working"
        DEVNULL = open(os.devnull, 'wb')

        system(f'mkdir -p "/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}"')
        if self.jobCodec == "x264" and not path.exists(f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/episode_x264.mp4") and not path.exists(f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/hls/x264/master.m3u8"):
            args = [f"../scripts/ffmpeg-x264-medium.sh", f"/usr/src/nyananime/src-episodes/{self.jobAnimeID}/{self.jobSrcFile}", f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}"]
            self.jobSubprocess = subprocess.Popen(args, stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
            self.jobSubprocess.wait()
        elif self.jobCodec == "vp9" and not path.exists(f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/episode_vp9.webm") and not path.exists(f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/hls/vp9/master.m3u8"):
            args = [f"../scripts/ffmpeg-vp9.sh", f"/usr/src/nyananime/src-episodes/{self.jobAnimeID}/{self.jobSrcFile}", f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}"]
            args.extend(self.jobVideoOptions)
            self.jobSubprocess = subprocess.Popen(args, stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
            self.jobSubprocess.wait()
        
        audioStreams = subprocess.getoutput(f'ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "/usr/src/nyananime/src-episodes/{self.jobAnimeID}/{self.jobSrcFile}" | wc -w')
        self.jobName = f"Generating HLS streams for '{self.jobSrcFile}' ({self.jobCodec})..."
        if self.jobCodec == "x264" and not path.exists(f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/hls/x264/master.m3u8"):
            system(f'mkdir -p "/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/hls/x264"')
            script = "../scripts/ffmpeg-x264-hls.sh" if int(audioStreams) <= 1 else "../scripts/ffmpeg-x264-hls-dub.sh"
            args = [script, f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/episode_x264.mp4", f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}"]
            self.jobSubprocess = subprocess.Popen(args, stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
            self.jobSubprocess.wait()
            # system(f'rm "/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/episode_x264.mp4"')
        elif self.jobCodec == "vp9" and not path.exists(f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/hls/vp9/master.m3u8"):
            system(f'mkdir -p "/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/hls/vp9"')
            script = "../scripts/ffmpeg-vp9-hls.sh" if int(audioStreams) <= 1 else "../scripts/ffmpeg-vp9-hls-dub.sh"
            args = [script, f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/episode_vp9.webm", f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}"]
            self.jobSubprocess = subprocess.Popen(args, stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
            self.jobSubprocess.wait()
            # system(f'rm "/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/episode_vp9.webm"')
        
        system(f'mkdir -p "/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/subs"')
        system(f'mkdir -p "/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/hls/subs"')
        subtitleStreams = subprocess.getoutput(f'ffprobe -v error -select_streams s -show_entries stream=index -of csv=p=0 "/usr/src/nyananime/src-episodes/{self.jobAnimeID}/{self.jobSrcFile}" | wc -w')
        duration = subprocess.getoutput(f'ffprobe -i "/usr/src/nyananime/src-episodes/{self.jobAnimeID}/{self.jobSrcFile}" -v quiet -show_entries format=duration -hide_banner -of default=noprint_wrappers=1:nokey=1')
        processedSubtitles = []
        self.jobName = f"Extracting subtitles ({subtitleStreams}) from '{self.jobSrcFile}'..."
        for i in range(int(subtitleStreams)):
            subtitleStreamLanguage = subprocess.getoutput(f'ffprobe -v error -select_streams s:{i} -show_entries stream=index:stream_tags=language -of csv=p=0 "/usr/src/nyananime/src-episodes/{self.jobAnimeID}/{self.jobSrcFile}"')
            if "," not in subtitleStreamLanguage:
                continue
            subtitleStreamLanguage = subtitleStreamLanguage[(subtitleStreamLanguage.index(",") + 1):]
            if subtitleStreamLanguage in processedSubtitles:
                continue
            processedSubtitles.append(subtitleStreamLanguage)

            if not path.exists(f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/subs/{subtitleStreamLanguage}.vtt"):
                self.jobSubprocess = subprocess.Popen(["../scripts/ffmpeg-subs.sh", f"/usr/src/nyananime/src-episodes/{self.jobAnimeID}/{self.jobSrcFile}", f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/subs/{subtitleStreamLanguage}.vtt", f"{i}"], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
                self.jobSubprocess.wait()
                self.jobSubprocess = subprocess.Popen(["../scripts/subs-clean.sh", f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/subs/{subtitleStreamLanguage}.vtt"], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
                self.jobSubprocess.wait()
                self.jobSubprocess = subprocess.Popen(["../scripts/subs-clean-ad.sh", f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/subs/{subtitleStreamLanguage}.vtt"], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
                self.jobSubprocess.wait()
            
            if not path.exists(f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/hls/subs/{subtitleStreamLanguage}.m3u8"):
                self.jobSubprocess = subprocess.Popen(["../scripts/subs-create-hls.sh", f"../../subs/{subtitleStreamLanguage}.vtt", duration, f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/hls/subs/{subtitleStreamLanguage}.m3u8"], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
                self.jobSubprocess.wait()
        
        masterLines = []
        self.jobName = f"Editing HLS playlists of '{self.jobSrcFile}'..."
        with open(f'/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/hls/{"x264" if self.jobCodec == "x264" else "vp9"}/master.m3u8') as f:
            masterLines = f.readlines()

            for i in range(len(masterLines)):
                if "#EXT-X-STREAM-INF" in masterLines[i] and ',SUBTITLES="subs"' not in masterLines[i]:
                    masterLines[i] = masterLines[i][:-1] + ',SUBTITLES="subs"\n'

            processedSubtitles = []
            for i in range(int(subtitleStreams)):
                subtitleStreamLanguage = subprocess.getoutput(f'ffprobe -v error -select_streams s:{i} -show_entries stream=index:stream_tags=language -of csv=p=0 "/usr/src/nyananime/src-episodes/{self.jobAnimeID}/{self.jobSrcFile}"')
                if "," not in subtitleStreamLanguage:
                    continue
                subtitleStreamLanguage = subtitleStreamLanguage[(subtitleStreamLanguage.index(",") + 1):]
                if subtitleStreamLanguage in processedSubtitles:
                    continue
                processedSubtitles.append(subtitleStreamLanguage)

                subtitleMedia = f'#EXT-X-MEDIA:TYPE=SUBTITLES,GROUP-ID="subs",NAME="{subtitleStreamLanguage}",DEFAULT={"YES" if subtitleStreamLanguage == "eng" else "NO"},FORCED=NO,URI="../subs/{subtitleStreamLanguage}.m3u8",LANGUAGE="{subtitleStreamLanguage}"'
                if subtitleMedia not in masterLines:
                    if i == 0:
                        masterLines.append("")
                    masterLines.append(subtitleMedia + "\n")

        with open(f'/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/hls/{"x264" if self.jobCodec == "x264" else "vp9"}/master.m3u8', "w") as f:
            f.writelines(masterLines)

        self.jobName = f"Generating thumbnail for '{self.jobSrcFile}'..."
        if not path.exists(f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/thumbnail.webp"):
            self.jobSubprocess = subprocess.Popen(["../scripts/ffmpeg-thumbnail.sh", f"/usr/src/nyananime/src-episodes/{self.jobAnimeID}/{self.jobSrcFile}", f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}"], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
            self.jobSubprocess.wait()

        self.jobName = f"Extracting chapters from '{self.jobSrcFile}'..."
        if not path.exists(f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/chapters.json"):
            self.jobSubprocess = subprocess.Popen(["../scripts/ffmpeg-chapters.sh", f"/usr/src/nyananime/src-episodes/{self.jobAnimeID}/{self.jobSrcFile}", f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}"], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
            self.jobSubprocess.wait()

        # if not path.exists(f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/stats.json"):
        #     self.jobLogs.append(f'Generating stats...')
        #     self.jobSubprocess = subprocess.Popen(["../scripts/ffmpeg-stats.sh", f"/usr/src/nyananime/src-episodes/{self.jobAnimeID}/{self.jobSrcFile}", f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}"], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
        #     self.jobSubprocess.wait()
        # else:
        #     self.jobLogs.append(f'Stats already generated. Skipping...')
        
        self.jobName = f"Transcoding job for '{self.jobSrcFile}'"
        self.jobStatus = "finished"
        DEVNULL.close()