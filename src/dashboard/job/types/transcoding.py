from datetime import timedelta
import subprocess, os
from iso639 import languages
from os import system, path
from job.job import Job

class TranscodingJob(Job):
    def __init__(self, dashboard, jobAnimeID, jobEpisodeIndex, jobSrcPath, jobCodec, jobVideoOptions):
        Job.__init__(self, dashboard, "transcoding")
        self.jobAnimeID = jobAnimeID
        self.jobEpisodeIndex = jobEpisodeIndex
        self.jobSrcPath = jobSrcPath
        self.jobSrcFrames = 0
        self.jobSrcSize = 0
        self.jobCodec = jobCodec
        self.jobVideoOptions = jobVideoOptions
        self.jobPath = f"{self.jobAnimeID}/{self.jobEpisodeIndex}" if self.jobEpisodeIndex != None else self.jobAnimeID
        self.jobName = f"Transcoding job for '{self.jobPath}'"

    def loadProgress(self):
        if self.jobSrcFrames == 0:
            frames = subprocess.getoutput(f'ffprobe -v error -select_streams v -show_entries stream=index:stream_tags=NUMBER_OF_FRAMES -of csv=p=0 "{self.jobSrcPath}"')
            if "," in frames:
                self.jobSrcFrames = int(frames[(frames.index(",") + 1):])
            else:
                # This is really slow btw, probably should replace it with duration based progress calculation, but Erai-Raws releases should work with the fast NUMBER_OF_FRAMES method
                frames = subprocess.getoutput(f'ffprobe -v error -select_streams v -count_packets -show_entries stream=nb_read_packets -of csv=p=0 "{self.jobSrcPath}"')
                try:
                    self.jobSrcFrames = int(frames)
                except:
                    self.jobSrcFrames = 1
        if self.jobSrcSize == 0:
            file_stats = os.stat(self.jobSrcPath)
            self.jobSrcSize = file_stats.st_size

    def runProgress(self):
        if self.jobSubprocess == None:
            return
        
        while self.jobSubprocess.stderr != None:
            line = str(self.jobSubprocess.stderr.readline())
            if not line: break
            try:
                if "frame=" in line:
                    frame = int(line[len("frame="):line.index("fps=")].strip())
                    fps = round(float(line[line.index("fps=")+len("fps="):line.index("q=")].strip()))
                    # q = line[line.index("q=")+len("q="):line.index("size=")-1].strip()
                    size = line[line.index("size=")+len("size="):line.index("time=")].strip()
                    bitrate = line[line.index("bitrate=")+len("bitrate="):line.index("speed=")].strip()
                    try:
                        speed = round(float(line[line.index("speed=")+len("speed="):line.index("\n")-1].strip()), 2)
                    except:
                        speed = "-"
                    try:
                        size_ratio = round(int(size[:-2]) / (self.jobSrcSize * (frame / self.jobSrcFrames)), 2)
                    except:
                        size_ratio = "-"
                    self.jobProgress = round((frame / self.jobSrcFrames) * 100, 2)
                    if speed == "-" or bitrate == "N/A":
                        self.jobDetails = f"{round(fps / 24, 2)}x ({fps} fps, {size}/{size_ratio}x)"
                    else:
                        self.jobDetails = f"{speed}x ({bitrate}, {size}/{size_ratio}x)"
                elif "VMAF score:" in line:
                    vmaf = round(float(line[line.index("score:")+len("score:"):line.index("\n")-1].strip()), 2)
                    with open(f'{self.dashboard.path}/dest-episodes/{self.jobPath}/vmaf_{self.jobCodec}.sql', "w") as f:
                        f.write(f'UPDATE encodes SET vmaf={vmaf} WHERE id="{self.jobAnimeID}-{self.jobEpisodeIndex}-{"0" if self.jobCodec == "x264" else "1"}"')
            except Exception as e:
                print(e)
                continue
        self.jobSubprocess.wait()

    # TODO: Add a check for PGS subtitles
    # TODO: Add a check for commentary second audio stream
    # TODO: Add a way to decide which one from 2 same language subtitles to use (bigger == the right one?)
    def run(self):
        DEVNULL = open(os.devnull, 'wb')
        self.startSection(f"Scanning '{self.jobPath}'...")
        self.loadProgress()
        self.endSection()

        system(f'mkdir -p "{self.dashboard.path}/dest-episodes/{self.jobPath}"')
        self.startSection(f"Transcoding '{self.jobPath}' ({self.jobCodec})...")
        if self.jobCodec == "x264" and not path.exists(f"{self.dashboard.path}/dest-episodes/{self.jobPath}/episode_x264.mp4") and not path.exists(f"{self.dashboard.path}/dest-episodes/{self.jobPath}/hls/x264/master.m3u8"):
            args = ["../scripts/ffmpeg-x264-medium.sh", self.jobSrcPath, f"{self.dashboard.path}/dest-episodes/{self.jobPath}"]
            self.jobSubprocess = subprocess.Popen(args, stdin=DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        elif self.jobCodec == "vp9" and not path.exists(f"{self.dashboard.path}/dest-episodes/{self.jobPath}/episode_vp9.webm") and not path.exists(f"{self.dashboard.path}/dest-episodes/{self.jobPath}/hls/vp9/master.m3u8"):
            args = ["../scripts/ffmpeg-vp9.sh", self.jobSrcPath, f"{self.dashboard.path}/dest-episodes/{self.jobPath}"]
            args.extend(self.jobVideoOptions)
            self.jobSubprocess = subprocess.Popen(args, stdin=DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        self.runProgress()
        self.endSection()
        
        if self.jobCodec == "x264":
            audioStreams = subprocess.getoutput(f'ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "{self.jobSrcPath}" | wc -w')
            if not path.exists(f"{self.dashboard.path}/dest-episodes/{self.jobPath}/hls/x264/master.m3u8"):
                system(f'mkdir -p "{self.dashboard.path}/dest-episodes/{self.jobPath}/hls/x264"')
                script = "../scripts/ffmpeg-x264-hls.sh" if int(audioStreams) <= 1 else "../scripts/ffmpeg-x264-hls-dub.sh"
                args = [script, f"{self.dashboard.path}/dest-episodes/{self.jobPath}/episode_x264.mp4", f"{self.dashboard.path}/dest-episodes/{self.jobPath}"]
                self.jobSubprocess = subprocess.Popen(args, stdin=DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                # system(f'rm "{self.dashboard.path}/dest-episodes/{self.jobPath}/episode_x264.mp4"')
            self.startSection(f"Generating HLS streams for '{self.jobPath}' ({self.jobCodec})...")
            self.runProgress()
            self.endSection()

            system(f'mkdir -p "{self.dashboard.path}/dest-episodes/{self.jobPath}/subs"')
            system(f'mkdir -p "{self.dashboard.path}/dest-episodes/{self.jobPath}/hls/subs"')
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

                if not path.exists(f"{self.dashboard.path}/dest-episodes/{self.jobPath}/subs/{subtitleStreamLanguage}.vtt"):
                    self.jobSubprocess = subprocess.Popen(["../scripts/ffmpeg-subs.sh", self.jobSrcPath, f"{self.dashboard.path}/dest-episodes/{self.jobPath}/subs/{subtitleStreamLanguage}.vtt", f"{i}"], stdin=DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                    self.startSection(f"Extracting subtitles ({subtitleStreamLanguage}, {i}/{subtitleStreams}) from '{self.jobPath}'...")
                    self.runProgress()
                    self.endSection()
                    self.jobSubprocess = subprocess.Popen(["../scripts/subs-clean.sh", f"{self.dashboard.path}/dest-episodes/{self.jobPath}/subs/{subtitleStreamLanguage}.vtt"], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
                    self.jobSubprocess.wait()
                    self.jobSubprocess = subprocess.Popen(["../scripts/subs-clean-ad.sh", f"{self.dashboard.path}/dest-episodes/{self.jobPath}/subs/{subtitleStreamLanguage}.vtt"], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
                    self.jobSubprocess.wait()
                
                if not path.exists(f"{self.dashboard.path}/dest-episodes/{self.jobPath}/hls/subs/{subtitleStreamLanguage}.m3u8"):
                    self.jobSubprocess = subprocess.Popen(["../scripts/subs-create-hls.sh", f"../../subs/{subtitleStreamLanguage}.vtt", duration, f"{self.dashboard.path}/dest-episodes/{self.jobPath}/hls/subs/{subtitleStreamLanguage}.m3u8"], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
                    self.jobSubprocess.wait()

                self.jobProgress = round((i / subtitleStreams) * 100, 2)
        
            masterLines = []
            self.startSection(f"Editing HLS playlists of '{self.jobPath}'...")
            with open(f'{self.dashboard.path}/dest-episodes/{self.jobPath}/hls/{self.jobCodec}/master.m3u8') as f:
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

            with open(f'{self.dashboard.path}/dest-episodes/{self.jobPath}/hls/{self.jobCodec}/master.m3u8', "w") as f:
                f.writelines(masterLines)
            self.endSection()

        self.startSection(f"Generating thumbnails for '{self.jobPath}'...")
        if not path.exists(f"{self.dashboard.path}/dest-episodes/{self.jobPath}/thumbnail.webp"):
            self.jobSubprocess = subprocess.Popen(["../scripts/ffmpeg-thumbnail.sh", self.jobSrcPath, f"{self.dashboard.path}/dest-episodes/{self.jobPath}"], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
            self.jobSubprocess.wait()
        self.endSection()

        self.startSection(f"Extracting chapters from '{self.jobPath}'...")
        if not path.exists(f"{self.dashboard.path}/dest-episodes/{self.jobPath}/chapters.json"):
            self.jobSubprocess = subprocess.Popen(["../scripts/ffmpeg-chapters.sh", self.jobSrcPath, f"{self.dashboard.path}/dest-episodes/{self.jobPath}"], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
            self.jobSubprocess.wait()
        self.endSection()

        self.startSection(f"Generating stats from '{self.jobPath}'...")
        if not path.exists(f"{self.dashboard.path}/dest-episodes/{self.jobPath}/stats_{self.jobCodec}.txt"):
            self.jobSubprocess = subprocess.Popen([f"../scripts/ffmpeg-{self.jobCodec}-stats.sh", f'{self.dashboard.path}/dest-episodes/{self.jobPath}/episode_{self.jobCodec}{"mp4" if self.jobCodec == "x264" else "webm"}', f"{self.dashboard.path}/dest-episodes/{self.jobPath}", f"{self.jobAnimeID}-{self.jobEpisodeIndex}"], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
            self.jobSubprocess.wait()
        self.endSection()

        self.startSection(f"Generating VMAF score from '{self.jobPath}'...")
        if not path.exists(f"{self.dashboard.path}/dest-episodes/{self.jobPath}/vmaf_{self.jobCodec}.sql"):
            self.jobSubprocess = subprocess.Popen([f"../scripts/ffmpeg-vmaf.sh", self.jobSrcPath, f'{self.dashboard.path}/dest-episodes/{self.jobPath}/episode_{self.jobCodec}.{"mp4" if self.jobCodec == "x264" else "webm"}'], stdin=DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        self.runProgress()
        self.endSection()

        self.startSection(f"Generating timeline from '{self.jobPath}'...")
        if not path.exists(f"{self.dashboard.path}/dest-episodes/{self.jobPath}/timeline_0.webp"):
            for n in range(0, self.jobSrcFrames, 120 * 6 * 6):
                time_second = round(n / 24)
                time = "{:0>8}".format(str(timedelta(seconds=time_second)))
                self.jobSubprocess = subprocess.Popen([f"../scripts/ffmpeg-timeline.sh", self.jobSrcPath, f"{self.dashboard.path}/dest-episodes/{self.jobPath}", time, str(time_second)], stdin=DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                self.jobSubprocess.wait()
                self.jobProgress = round((n / self.jobSrcFrames) * 100, 2)
        self.endSection()

        self.jobName = f"Transcoding job for '{self.jobPath}'"
        DEVNULL.close()