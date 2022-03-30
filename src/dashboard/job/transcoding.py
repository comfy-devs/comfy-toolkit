import subprocess, os
from iso639 import languages
from os import system, path
from util.general import colorize
from job.job import Job

class TranscodingJob(Job):
    def __init__(self, jobAnimeID, jobEpisodeIndex, jobSrcPath, jobCodec, jobVideoOptions):
        Job.__init__(self, "transcoding")
        self.jobAnimeID = jobAnimeID
        self.jobEpisodeIndex = jobEpisodeIndex
        self.jobSrcPath = jobSrcPath
        self.jobSrcFrames = None
        self.jobCodec = jobCodec
        self.jobVideoOptions = jobVideoOptions
        self.jobPath = f"/{self.jobEpisodeIndex}" if self.jobEpisodeIndex != None else ""
        self.jobName = f"Transcoding job for '{self.jobAnimeID}{self.jobPath}'"

    def runProgress(self):
        if self.jobSubprocess == None:
            return
        
        if self.jobSrcFrames == None:
            self.jobSrcFrames = subprocess.getoutput(f'ffprobe -v error -select_streams v -show_entries stream=index:stream_tags=NUMBER_OF_FRAMES -of csv=p=0 "{self.jobSrcPath}"')
            if "," in self.jobSrcFrames:
                self.jobSrcFrames = int(self.jobSrcFrames[(self.jobSrcFrames.index(",") + 1):])
            else:
                # This is really slow btw, probably should replace it with duration based progress calculation, but Erai-Raws releases should work with the fast NUMBER_OF_FRAMES method
                self.jobSrcFrames = subprocess.getoutput(f'ffprobe -v error -select_streams v -count_packets -show_entries stream=nb_read_packets -of csv=p=0 "{self.jobSrcPath}"')
                try:
                    self.jobSrcFrames = int(self.jobSrcFrames)
                except:
                    self.jobSrcFrames = 1

        while True:
            line = self.jobSubprocess.stderr.readline()
            if not line: break
            try:
                if "frame=" in line:
                    currentFrame = int(line[len("frame="):line.index("fps=")])
                    self.jobProgress = round((currentFrame / self.jobSrcFrames) * 100, 2)
                    self.jobSpeed = line[line.index("speed=")+len("speed="):line.index("\n")].strip()
            except:
                continue
        self.jobSubprocess.wait()

    # TODO: Add a check for PGS subtitles
    # TODO: Add a check for commentary second audio stream
    # TODO: Add a way to decide which one from 2 same language subtitles to use (bigger == the right one?)
    def run(self):
        DEVNULL = open(os.devnull, 'wb')

        system(f'mkdir -p "/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}"')
        if self.jobCodec == "x264" and not path.exists(f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/episode_x264.mp4") and not path.exists(f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/hls/x264/master.m3u8"):
            args = [f"../scripts/ffmpeg-x264-medium.sh", self.jobSrcPath, f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}"]
            self.jobSubprocess = subprocess.Popen(args, stdin=DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines='\r')
        elif self.jobCodec == "vp9" and not path.exists(f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/episode_vp9.webm") and not path.exists(f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/hls/vp9/master.m3u8"):
            args = [f"../scripts/ffmpeg-vp9.sh", self.jobSrcPath, f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}"]
            args.extend(self.jobVideoOptions)
            self.jobSubprocess = subprocess.Popen(args, stdin=DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines='\r')
        self.startSection(f"Transcoding '{self.jobAnimeID}{self.jobPath}' ({self.jobCodec})...")
        self.runProgress()
        self.endSection()
        
        audioStreams = subprocess.getoutput(f'ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "{self.jobSrcPath}" | wc -w')
        if self.jobCodec == "x264" and not path.exists(f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/hls/x264/master.m3u8"):
            system(f'mkdir -p "/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/hls/x264"')
            script = "../scripts/ffmpeg-x264-hls.sh" if int(audioStreams) <= 1 else "../scripts/ffmpeg-x264-hls-dub.sh"
            args = [script, f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/episode_x264.mp4", f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}"]
            self.jobSubprocess = subprocess.Popen(args, stdin=DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines='\r')
            # system(f'rm "/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/episode_x264.mp4"')
        elif self.jobCodec == "vp9" and not path.exists(f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/hls/vp9/master.m3u8"):
            system(f'mkdir -p "/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/hls/vp9"')
            script = "../scripts/ffmpeg-vp9-hls.sh" if int(audioStreams) <= 1 else "../scripts/ffmpeg-vp9-hls-dub.sh"
            args = [script, f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/episode_vp9.webm", f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}"]
            self.jobSubprocess = subprocess.Popen(args, stdin=DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines='\r')
            # system(f'rm "/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/episode_vp9.webm"')
        self.startSection(f"Generating HLS streams for '{self.jobAnimeID}{self.jobPath}' ({self.jobCodec})...")
        self.runProgress()
        self.endSection()
        
        system(f'mkdir -p "/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/subs"')
        system(f'mkdir -p "/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/hls/subs"')
        subtitleStreams = int(subprocess.getoutput(f'ffprobe -v error -select_streams s -show_entries stream=index -of csv=p=0 "{self.jobSrcPath}" | wc -w'))
        duration = subprocess.getoutput(f'ffprobe -i "{self.jobSrcPath}" -v quiet -show_entries format=duration -hide_banner -of default=noprint_wrappers=1:nokey=1')
        processedSubtitles = []
        for i in range(subtitleStreams):
            subtitleStreamLanguage = subprocess.getoutput(f'ffprobe -v error -select_streams s:{i} -show_entries stream=index:stream_tags=language -of csv=p=0 "{self.jobSrcPath}"')
            if "," in subtitleStreamLanguage:
                subtitleStreamLanguage = subtitleStreamLanguage[(subtitleStreamLanguage.index(",") + 1):]
            else:
                subtitleStreamLanguage = "eng"
            if subtitleStreamLanguage in processedSubtitles:
                continue
            processedSubtitles.append(subtitleStreamLanguage)

            if not path.exists(f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/subs/{subtitleStreamLanguage}.vtt"):
                self.jobSubprocess = subprocess.Popen(["../scripts/ffmpeg-subs.sh", self.jobSrcPath, f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/subs/{subtitleStreamLanguage}.vtt", f"{i}"], stdin=DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines='\r')
                self.startSection(f"Extracting subtitles ({subtitleStreamLanguage}, {i}/{subtitleStreams}) from '{self.jobAnimeID}{self.jobPath}'...")
                self.runProgress()
                self.endSection()
                self.jobSubprocess = subprocess.Popen(["../scripts/subs-clean.sh", f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/subs/{subtitleStreamLanguage}.vtt"], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
                self.jobSubprocess.wait()
                self.jobSubprocess = subprocess.Popen(["../scripts/subs-clean-ad.sh", f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/subs/{subtitleStreamLanguage}.vtt"], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
                self.jobSubprocess.wait()
            
            if not path.exists(f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/hls/subs/{subtitleStreamLanguage}.m3u8"):
                self.jobSubprocess = subprocess.Popen(["../scripts/subs-create-hls.sh", f"../../subs/{subtitleStreamLanguage}.vtt", duration, f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/hls/subs/{subtitleStreamLanguage}.m3u8"], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
                self.jobSubprocess.wait()

            self.jobProgress = round((i / subtitleStreams) * 100, 2)
        
        
        masterLines = []
        self.startSection(f"Editing HLS playlists of '{self.jobAnimeID}{self.jobPath}'...")
        with open(f'/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/hls/{"x264" if self.jobCodec == "x264" else "vp9"}/master.m3u8') as f:
            masterLines = f.readlines()

            for i in range(len(masterLines)):
                if "#EXT-X-STREAM-INF" in masterLines[i] and ',SUBTITLES="subs"' not in masterLines[i]:
                    masterLines[i] = masterLines[i][:-1] + ',SUBTITLES="subs"\n'

            processedSubtitles = []
            for i in range(int(subtitleStreams)):
                subtitleStreamLanguage = subprocess.getoutput(f'ffprobe -v error -select_streams s:{i} -show_entries stream=index:stream_tags=language -of csv=p=0 "{self.jobSrcPath}"')
                if "," in subtitleStreamLanguage:
                    subtitleStreamLanguage = subtitleStreamLanguage[(subtitleStreamLanguage.index(",") + 1):]
                else:
                    subtitleStreamLanguage = "eng"
                if subtitleStreamLanguage in processedSubtitles:
                    continue
                processedSubtitles.append(subtitleStreamLanguage)

                subtitleMedia = f'#EXT-X-MEDIA:TYPE=SUBTITLES,GROUP-ID="subs",NAME="{languages.get(part2b=subtitleStreamLanguage).name}",DEFAULT={"YES" if subtitleStreamLanguage == "eng" else "NO"},FORCED=NO,URI="../subs/{subtitleStreamLanguage}.m3u8",LANGUAGE="{subtitleStreamLanguage}"\n'
                if subtitleMedia not in masterLines:
                    masterLines.append(subtitleMedia)

        with open(f'/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/hls/{"x264" if self.jobCodec == "x264" else "vp9"}/master.m3u8', "w") as f:
            f.writelines(masterLines)
        self.endSection()

        self.startSection(f"Generating thumbnails for '{self.jobAnimeID}{self.jobPath}'...")
        if not path.exists(f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/thumbnail.webp"):
            self.jobSubprocess = subprocess.Popen(["../scripts/ffmpeg-thumbnail.sh", self.jobSrcPath, f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}", "webp"], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
            self.jobSubprocess.wait()
        if not path.exists(f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/thumbnail.jpg"):
            self.jobSubprocess = subprocess.Popen(["../scripts/ffmpeg-thumbnail.sh", self.jobSrcPath, f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}", "jpg"], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
            self.jobSubprocess.wait()
        self.endSection()

        self.startSection(f"Extracting chapters from '{self.jobAnimeID}{self.jobPath}'...")
        if not path.exists(f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/chapters.json"):
            self.jobSubprocess = subprocess.Popen(["../scripts/ffmpeg-chapters.sh", self.jobSrcPath, f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}"], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
            self.jobSubprocess.wait()
        self.endSection()

        # if not path.exists(f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}/stats.json"):
        #     self.jobLogs.append(f'Generating stats...')
        #     self.jobSubprocess = subprocess.Popen(["../scripts/ffmpeg-stats.sh", f"/usr/src/nyananime/src-episodes/{self.jobAnimeID}/{self.jobSrcFile}", f"/usr/src/nyananime/dest-episodes/{self.jobAnimeID}/{self.jobEpisodeIndex}"], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
        #     self.jobSubprocess.wait()
        # else:
        #     self.jobLogs.append(f'Stats already generated. Skipping...')
        
        self.jobName = f"Transcoding job for '{self.jobAnimeID}{self.jobPath}'"
        DEVNULL.close()