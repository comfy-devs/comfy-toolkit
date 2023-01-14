from datetime import timedelta
from itertools import groupby
import json
import subprocess, os
from iso639 import languages
from os import system, path
from job.job import Job

class TranscodingJob(Job):
    def __init__(self, dashboard, jobShowID, jobEpisodeIndex, jobSrcPath, jobCodec, jobTune, jobVideoOptions):
        Job.__init__(self, dashboard, "transcoding")
        self.jobShowID = jobShowID
        self.jobEpisodeIndex = jobEpisodeIndex
        self.jobSrcPath = jobSrcPath
        self.jobSrcFrames = 0
        self.jobSrcFramerate = 0
        self.jobSrcSize = 0
        self.jobCodec = jobCodec
        self.jobTune = jobTune
        self.jobCodecEnum = 0 if jobCodec == "x264" else 1
        self.jobCodecEpisodeName = f'episode_{self.jobCodec}.{"mp4" if self.jobCodec == "x264" else "webm"}'
        self.jobVideoOptions = jobVideoOptions
        self.jobPath = f"{self.jobShowID}/{self.jobEpisodeIndex}"
        self.jobName = f"Transcoding job for '{self.jobPath}'"

    def loadProgress(self):
        if self.jobSrcFrames == 0:
            frames = subprocess.getoutput(f'ffprobe -v error -select_streams v -show_entries stream=index:stream_tags=NUMBER_OF_FRAMES -of csv=p=0 "{self.dashboard.fileSystem.getFile(self.jobSrcPath)}"')
            if "," in frames:
                self.jobSrcFrames = int(frames[(frames.index(",") + 1):])
            else:
                # This is really slow btw, probably should replace it with duration based progress calculation, but Erai-Raws releases should work with the fast NUMBER_OF_FRAMES method
                frames = subprocess.getoutput(f'ffprobe -v error -select_streams v -count_packets -show_entries stream=nb_read_packets -of csv=p=0 "{self.dashboard.fileSystem.getFile(self.jobSrcPath)}"')
                try:
                    self.jobSrcFrames = int(frames)
                except:
                    self.jobSrcFrames = 1
        if self.jobSrcFramerate == 0:
            framerate = subprocess.getoutput(f'ffprobe -v error -select_streams v -show_entries stream=avg_frame_rate -of csv=p=0 "{self.dashboard.fileSystem.getFile(self.jobSrcPath)}"')
            self.jobSrcFramerate = round(eval(framerate), 3)
        if self.jobSrcSize == 0:
            file_stats = os.stat(self.dashboard.fileSystem.getFile(self.jobSrcPath))
            self.jobSrcSize = file_stats.st_size

    def runProgress(self):
        if self.jobSubprocess == None:
            return
        
        self.loadProgress()
        while self.jobSubprocess.stderr != None:
            line = str(self.jobSubprocess.stderr.readline())
            if not line: break
            try:
                if "frame=" in line:
                    # Parse all data from ffmpeg output and figure out according details and progress
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
                        self.jobDetails = f"{round(fps / self.jobSrcFramerate, 2)}x ({fps} fps, {size}/{size_ratio}x)"
                    else:
                        self.jobDetails = f"{speed}x ({bitrate}, {size}/{size_ratio}x)"
                elif "VMAF score:" in line:
                    # This is used to save output from "ffmpeg-vmaf.sh", because we want both progress and output
                    vmaf = round(float(line[line.index("score:")+len("score:"):line.index("\n")-1].strip()), 2)
                    with open(f'{self.dashboard.fileSystem.basePath}/misc/{self.jobPath}/stats_{self.jobCodec}_vmaf.sql', "w") as f:
                        f.write(f'UPDATE encodes SET vmaf={vmaf} WHERE id="{self.jobShowID}-{self.jobEpisodeIndex}-{self.jobCodecEnum}";')
            except Exception as e:
                print(e)
                continue
        self.jobSubprocess.wait()

    def getSubtitleDetails(self):
        subtitleStreams = int(subprocess.getoutput(f'ffprobe -v error -select_streams s -show_entries stream=index -of csv=p=0 "{self.dashboard.fileSystem.getFile(self.jobSrcPath)}" | wc -w'))
        subtitleTracks = []
        for i in range(subtitleStreams):
            subtitleStreamLanguage = subprocess.getoutput(f'ffprobe -v error -select_streams s:{i} -show_entries stream=index:stream_tags=language -of csv=p=0 "{self.dashboard.fileSystem.getFile(self.jobSrcPath)}"')
            if "," in subtitleStreamLanguage:
                subtitleStreamLanguage = subtitleStreamLanguage[(subtitleStreamLanguage.index(",") + 1):]
            else:
                subtitleStreamLanguage = "eng"
            # TODO: this no work
            if subtitleStreamLanguage in subtitleTracks:
                continue
            subtitleStreamCodec = subprocess.getoutput(f'ffprobe -v error -select_streams s:{i} -show_entries stream=codec_name -of csv=p=0 "{self.dashboard.fileSystem.getFile(self.jobSrcPath)}"')
            if subtitleStreamCodec == "subrip":
                subtitleStreamCodec = "srt"
            subtitleTracks.append({ "pos": i, "lang": subtitleStreamLanguage, "codec": subtitleStreamCodec })
        
        return {
            "tracks": subtitleTracks
        }

    def getAudioDetails(self):
        audioStreams = int(subprocess.getoutput(f'ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "{self.dashboard.fileSystem.getFile(self.jobSrcPath)}" | wc -w'))
        audioTracks = []
        for i in range(audioStreams):
            audioStreamLanguage = subprocess.getoutput(f'ffprobe -v error -select_streams a:{i} -show_entries stream=index:stream_tags=language -of csv=p=0 "{self.dashboard.fileSystem.getFile(self.jobSrcPath)}"')
            if "," in audioStreamLanguage:
                audioStreamLanguage = audioStreamLanguage[(audioStreamLanguage.index(",") + 1):]
            else:
                audioStreamLanguage = "jpn"
            # TODO: this no work
            if audioStreamLanguage in audioTracks:
                continue
            audioTracks.append({ "pos": i, "lang": audioStreamLanguage })
        audioMappings = "-map 0:a"
        if audioStreams > 1 and audioTracks[0] == "eng":
            audioMappings = "-map 0:a:1 -map 0:a:0"
            audioTracks[0]["pos"] = 1
            audioTracks[1]["pos"] = 0
            audioTracks = [audioTracks[1], audioTracks[0]]
        
        return {
            "tracks": audioTracks,
            "mappings": audioMappings
        }

    # TODO: Add a check for PGS subtitles
    # TODO: Add a way to decide the corrent subtitle stream (so songs don't override main track)
    def run(self):
        DEVNULL = open(os.devnull, 'wb')
        system(f'mkdir -p "{self.dashboard.fileSystem.mountPath}/processed/{self.jobPath}"')
        system(f'mkdir -p "{self.dashboard.fileSystem.basePath}/misc/{self.jobPath}"')
        subtitleDetails = None
        audioDetails = None

        # Transcode source video based on chosen codec
        self.startSection(f"Transcoding '{self.jobPath}' ({self.jobCodec})...")
        if self.jobCodec == "x264" and not path.exists(f"{self.dashboard.fileSystem.basePath}/processed/{self.jobPath}/episode_x264.mp4"):
            audioDetails = self.getAudioDetails() if audioDetails == None else audioDetails
            args = ["../scripts/ffmpeg-x264-medium.sh", self.dashboard.fileSystem.getFile(self.jobSrcPath), f"{self.dashboard.fileSystem.mountPath}/processed/{self.jobPath}", self.jobTune, f"{round(self.jobSrcFramerate)}", audioDetails["mappings"]]
            self.jobSubprocess = subprocess.Popen(args, stdin=DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        elif self.jobCodec == "vp9" and not path.exists(f"{self.dashboard.fileSystem.basePath}/processed/{self.jobPath}/episode_vp9.webm"):
            audioDetails = self.getAudioDetails() if audioDetails == None else audioDetails
            args = ["../scripts/ffmpeg-vp9.sh", self.dashboard.fileSystem.getFile(self.jobSrcPath), f"{self.dashboard.fileSystem.mountPath}/processed/{self.jobPath}", *self.jobVideoOptions, audioDetails["mappings"]]
            self.jobSubprocess = subprocess.Popen(args, stdin=DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        self.runProgress()
        self.endSection()
        
        # Generate HLS video streams and playlists, if applicable
        self.startSection(f"Generating video HLS streams for '{self.jobPath}' ({self.jobCodec})...")
        if self.jobCodec == "x264" and not path.exists(f"{self.dashboard.fileSystem.basePath}/processed/{self.jobPath}/hls/x264/master.m3u8"):
            system(f'mkdir -p "{self.dashboard.fileSystem.basePath}/processed/{self.jobPath}/hls/x264"')
            args = ["../scripts/ffmpeg-x264-hls.sh", self.dashboard.fileSystem.getFile(f"processed/{self.jobPath}/episode_x264.mp4"), f"{self.dashboard.fileSystem.basePath}/processed/{self.jobPath}"]
            self.jobSubprocess = subprocess.Popen(args, stdin=DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            # system(f'rm "{self.dashboard.fileSystem.basePath}/processed/{self.jobPath}/episode_x264.mp4"')
        self.runProgress()
        self.endSection()

        # Generate HLS audio streams and playlists, if applicable
        self.startSection(f"Generating audio HLS streams for '{self.jobPath}'...")
        if not os.path.exists(f"{self.dashboard.fileSystem.basePath}/processed/{self.jobPath}/hls/audio"):
            system(f'mkdir -p "{self.dashboard.fileSystem.basePath}/processed/{self.jobPath}/hls/audio"')
            audioDetails = self.getAudioDetails() if audioDetails == None else audioDetails
            audioStreams = len(audioDetails["tracks"])
            for i in range(audioStreams):
                audioStream = audioDetails["tracks"][i]
                audioStreamLanguage = audioStream["lang"]
                if not path.exists(f"{self.dashboard.fileSystem.basePath}/processed/{self.jobPath}/hls/audio/0/{audioStreamLanguage}.m3u8"):
                    self.startSection(f"Generating audio HLS streams ({audioStreamLanguage}, {i+1}/{audioStreams}) for '{self.jobPath}'...")
                    self.jobSubprocess = subprocess.Popen(["../scripts/ffmpeg-audio-hls.sh", self.dashboard.fileSystem.getFile(f"processed/{self.jobPath}/episode_x264.mp4"), f"{self.dashboard.fileSystem.basePath}/processed/{self.jobPath}", str(audioStream["pos"]), audioStreamLanguage], stdin=DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                    self.runProgress()
                    self.endSection()
                self.jobProgress = round((i / audioStreams) * 100, 2)
        self.endSection()

        # Extract source video's subtitle tracks and create their HLS playlists
        self.startSection(f"Extracting subtitles from '{self.jobPath}'...")
        if not os.path.exists(f"{self.dashboard.fileSystem.basePath}/processed/{self.jobPath}/subs"):
            system(f'mkdir -p "{self.dashboard.fileSystem.basePath}/processed/{self.jobPath}/subs"')
            system(f'mkdir -p "{self.dashboard.fileSystem.basePath}/processed/{self.jobPath}/subs/original"')
            system(f'mkdir -p "{self.dashboard.fileSystem.basePath}/processed/{self.jobPath}/hls/subs"')
            duration = subprocess.getoutput(f'ffprobe -i "{self.dashboard.fileSystem.getFile(self.jobSrcPath)}" -v quiet -show_entries format=duration -hide_banner -of default=noprint_wrappers=1:nokey=1')
            subtitleDetails = self.getSubtitleDetails() if subtitleDetails == None else subtitleDetails
            subtitleStreams = len(subtitleDetails["tracks"])
            for i in range(subtitleStreams):
                subtitleStream = subtitleDetails["tracks"][i]
                subtitleStreamLanguage = subtitleStream["lang"]
                subtitleStreamCodec = subtitleStream["codec"]
                if not path.exists(f"{self.dashboard.fileSystem.basePath}/processed/{self.jobPath}/subs/{subtitleStreamLanguage}.vtt"):
                    self.startSection(f"Extracting subtitles ({subtitleStreamLanguage}, {i+1}/{subtitleStreams}) from '{self.jobPath}'...")
                    self.jobSubprocess = subprocess.Popen(["../scripts/ffmpeg-subs.sh", self.dashboard.fileSystem.getFile(self.jobSrcPath), f"{self.dashboard.fileSystem.basePath}/processed/{self.jobPath}/subs/original/{subtitleStreamLanguage}.{subtitleStreamCodec}", f"{i}"], stdin=DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                    self.runProgress()
                    self.jobSubprocess = subprocess.Popen(["../scripts/ffmpeg-subs.sh", self.dashboard.fileSystem.getFile(self.jobSrcPath), f"{self.dashboard.fileSystem.basePath}/processed/{self.jobPath}/subs/{subtitleStreamLanguage}.vtt", f"{i}"], stdin=DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                    self.runProgress()
                    self.jobSubprocess = subprocess.Popen(["../scripts/subs-clean.sh", f"{self.dashboard.fileSystem.basePath}/processed/{self.jobPath}/subs/{subtitleStreamLanguage}.vtt"], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
                    self.jobSubprocess.wait()
                    self.jobSubprocess = subprocess.Popen(["../scripts/subs-clean-ad.sh", f"{self.dashboard.fileSystem.basePath}/processed/{self.jobPath}/subs/{subtitleStreamLanguage}.vtt"], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
                    self.jobSubprocess.wait()
                    self.endSection()
                if not path.exists(f"{self.dashboard.fileSystem.basePath}/processed/{self.jobPath}/hls/subs/{subtitleStreamLanguage}.m3u8"):
                    self.jobSubprocess = subprocess.Popen(["../scripts/subs-create-hls.sh", f"../../subs/{subtitleStreamLanguage}.vtt", duration, f"{self.dashboard.fileSystem.basePath}/processed/{self.jobPath}/hls/subs/{subtitleStreamLanguage}.m3u8"], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
                    self.jobSubprocess.wait()
                self.jobProgress = round((i / subtitleStreams) * 100, 2)
        self.endSection()

        # Create .sql manifest to keep track of episode's audio tracks
        if not os.path.exists(f"{self.dashboard.fileSystem.basePath}/misc/{self.jobPath}/tracks.sql"):
            with open(f"{self.dashboard.fileSystem.basePath}/misc/{self.jobPath}/tracks.sql", "w") as f:
                subtitleDetails = self.getSubtitleDetails() if subtitleDetails == None else subtitleDetails
                subtitleList = ",".join(map(lambda t: t["lang"], subtitleDetails["tracks"]))
                audioDetails = self.getAudioDetails() if audioDetails == None else audioDetails
                audioList = ",".join(map(lambda t: t["lang"], audioDetails["tracks"]))
                f.write(f'UPDATE episodes SET subtitles="{subtitleList}", audio="{audioList}" WHERE id="{self.jobShowID}-{self.jobEpisodeIndex}";')
        
        # Edit master HLS playlist, if applicable
        self.startSection(f"Editing master HLS playlist of '{self.jobPath}'...")
        if self.jobCodec == "x264" and not os.path.exists(f"{self.dashboard.fileSystem.basePath}/processed/{self.jobPath}/hls/{self.jobCodec}/master_original.m3u8"):
            masterLines = []
            with open(f"{self.dashboard.fileSystem.basePath}/processed/{self.jobPath}/hls/{self.jobCodec}/master.m3u8") as playlistFile:
                masterLines = playlistFile.readlines()
                for i in range(len(masterLines)):
                    if "#EXT-X-STREAM-INF" in masterLines[i]:
                        level = 0
                        if "1280x720" in masterLines[i]:
                            level = 1
                        elif "854x480" in masterLines[i]:
                            level = 2
                        if ',SUBTITLES="subs"' not in masterLines[i]:
                            masterLines[i] = masterLines[i][:-1] + ',SUBTITLES="subs"\n'
                        if f',AUDIO="audio-{level}"' not in masterLines[i]:
                            masterLines[i] = masterLines[i][:-1] + f',AUDIO="audio-{level}"\n'
                subtitleDetails = self.getSubtitleDetails() if subtitleDetails == None else subtitleDetails
                for i in range(len(subtitleDetails["tracks"])):
                    subtitleStream = subtitleDetails["tracks"][i]
                    subtitleStreamLanguage = subtitleStream["lang"]
                    subtitleMedia = f'#EXT-X-MEDIA:TYPE=SUBTITLES,GROUP-ID="subs",NAME="{languages.get(part2b=subtitleStreamLanguage).name}",DEFAULT={"YES" if subtitleStreamLanguage == "eng" else "NO"},FORCED=NO,URI="../subs/{subtitleStreamLanguage}.m3u8",LANGUAGE="{subtitleStreamLanguage}"\n'
                    if subtitleMedia not in masterLines:
                        masterLines.append(subtitleMedia)
                audioDetails = self.getAudioDetails() if audioDetails == None else audioDetails
                for i in range(len(audioDetails["tracks"])):
                    audioStream = audioDetails["tracks"][i]
                    audioStreamLanguage = audioStream["lang"]
                    audioMedia = [
                        f'#EXT-X-MEDIA:TYPE=AUDIO,GROUP-ID="audio-0",NAME="{languages.get(part2b=audioStreamLanguage).name}",DEFAULT={"YES" if audioStreamLanguage == "eng" else "NO"},FORCED=NO,URI="../audio/0/{audioStreamLanguage}.m3u8",LANGUAGE="{audioStreamLanguage}"\n',
                        f'#EXT-X-MEDIA:TYPE=AUDIO,GROUP-ID="audio-1",NAME="{languages.get(part2b=audioStreamLanguage).name}",DEFAULT={"YES" if audioStreamLanguage == "eng" else "NO"},FORCED=NO,URI="../audio/1/{audioStreamLanguage}.m3u8",LANGUAGE="{audioStreamLanguage}"\n',
                        f'#EXT-X-MEDIA:TYPE=AUDIO,GROUP-ID="audio-2",NAME="{languages.get(part2b=audioStreamLanguage).name}",DEFAULT={"YES" if audioStreamLanguage == "eng" else "NO"},FORCED=NO,URI="../audio/2/{audioStreamLanguage}.m3u8",LANGUAGE="{audioStreamLanguage}"\n'
                    ]
                    if audioMedia not in masterLines:
                        masterLines.extend(audioMedia)
            system(f'mv "{self.dashboard.fileSystem.basePath}/processed/{self.jobPath}/hls/{self.jobCodec}/master.m3u8" "{self.dashboard.fileSystem.basePath}/processed/{self.jobPath}/hls/{self.jobCodec}/master_original.m3u8"')
            with open(f'{self.dashboard.fileSystem.basePath}/processed/{self.jobPath}/hls/{self.jobCodec}/master.m3u8', "w") as playlistFile:
                playlistFile.writelines(masterLines)
        self.endSection()

        # Generate episode's thumbnails
        self.startSection(f"Generating thumbnails for '{self.jobPath}'...")
        if not path.exists(f"{self.dashboard.fileSystem.basePath}/processed/{self.jobPath}/thumbnail.webp"):
            self.jobSubprocess = subprocess.Popen(["../scripts/ffmpeg-thumbnail.sh", self.dashboard.fileSystem.getFile(self.jobSrcPath), f"{self.dashboard.fileSystem.basePath}/processed/{self.jobPath}"], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
            self.jobSubprocess.wait()
        self.endSection()

        # Generate episode's timeline in form of spritesheets
        self.startSection(f"Generating timeline from '{self.jobPath}'...")
        if not path.exists(f"{self.dashboard.fileSystem.basePath}/processed/{self.jobPath}/timeline_0.webp"):
            self.loadProgress()
            timelineInterval = round(self.jobSrcFramerate) * 5
            for n in range(0, self.jobSrcFrames, timelineInterval * 6 * 6):
                time_second = round(n / round(self.jobSrcFramerate))
                time = "{:0>8}".format(str(timedelta(seconds=time_second)))
                self.jobSubprocess = subprocess.Popen([f"../scripts/ffmpeg-timeline.sh", self.dashboard.fileSystem.getFile(self.jobSrcPath), f"{self.dashboard.fileSystem.basePath}/processed/{self.jobPath}", time, str(time_second), str(timelineInterval)], stdin=DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                self.jobSubprocess.wait()
                self.jobProgress = round((n / self.jobSrcFrames) * 100, 2)
        self.endSection()

        # Extract episode's chapters
        self.startSection(f"Extracting chapters from '{self.jobPath}'...")
        if not path.exists(f"{self.dashboard.fileSystem.basePath}/processed/{self.jobPath}/chapters.json"):
            self.jobSubprocess = subprocess.Popen(["../scripts/ffmpeg-chapters.sh", self.dashboard.fileSystem.getFile(self.jobSrcPath), f"{self.dashboard.fileSystem.basePath}/processed/{self.jobPath}"], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
            self.jobSubprocess.wait()
        self.endSection()

        # Transform episode's chapters to .sql
        if not path.exists(f"{self.dashboard.fileSystem.basePath}/misc/{self.jobPath}/chapters.sql"):
            segments = []
            with open(os.path.join(self.dashboard.currentPath, "segments.json"), "r") as f:
                segments = json.loads(f.read())
            chapters = []
            with open(f"{self.dashboard.fileSystem.basePath}/processed/{self.jobPath}/chapters.json", "r") as f:
                self.i = 0
                def transformChapter(c):
                    t = segments[c["tags"]["title"]] if c["tags"]["title"] in segments else 1
                    return { "type": t, "start": round(float(c["start_time"])), "end": round(float(c["end_time"])) }
                def processChapterGroup(k, g):
                    length = g[len(g) - 1]["end"] - g[0]["start"]
                    result = f'INSERT IGNORE INTO segments (id, pos, episode, `type`, `length`) VALUES ("{self.jobShowID}-{self.jobEpisodeIndex}-{self.i}", {self.i}, "{self.jobShowID}-{self.jobEpisodeIndex}", {k}, {length});'
                    self.i += 1
                    return result
                chapters = json.loads(f.read())["chapters"]
                chapters = [transformChapter(c) for c in chapters]
                chapters = [processChapterGroup(k, list(g)) for k, g in groupby(chapters, key=lambda x: x["type"])]
            with open(f"{self.dashboard.fileSystem.basePath}/misc/{self.jobPath}/chapters.sql", "w") as f:
                f.write("\n".join(chapters))

        # Extract episode's attachments
        self.startSection(f"Extracting attachments for '{self.jobPath}'...")
        if not path.exists(f"{self.dashboard.fileSystem.basePath}/processed/{self.jobPath}/attachments"):
            system(f'mkdir -p "{self.dashboard.fileSystem.basePath}/processed/{self.jobPath}/attachments"')
            self.jobSubprocess = subprocess.Popen(["../scripts/ffmpeg-attachments.sh", self.dashboard.fileSystem.getFile(self.jobSrcPath), f"{self.dashboard.fileSystem.basePath}/processed/{self.jobPath}"], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
            self.jobSubprocess.wait()
        self.endSection()

        # Generate episode's stats and save as .sql (bitrate, duration, ...)
        self.startSection(f"Generating stats from '{self.jobPath}'...")
        if not path.exists(f"{self.dashboard.fileSystem.basePath}/misc/{self.jobPath}/stats_{self.jobCodec}.sql"):
            self.loadProgress()
            episodePath = self.dashboard.fileSystem.getFile(f"processed/{self.jobPath}/{self.jobCodecEpisodeName}")
            self.jobSubprocess = subprocess.Popen([f"../scripts/ffmpeg-stats.sh", episodePath, f"{self.dashboard.fileSystem.basePath}/misc/{self.jobPath}/stats_{self.jobCodec}.sql", f"{self.jobShowID}-{self.jobEpisodeIndex}", str(self.jobCodecEnum), str(self.jobSrcFramerate)], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
            self.jobSubprocess.wait()
        self.endSection()

        # Generate episode's VMAF quality score and save as .sql
        self.startSection(f"Generating VMAF score from '{self.jobPath}'...")
        if not path.exists(f"{self.dashboard.fileSystem.basePath}/misc/{self.jobPath}/stats_{self.jobCodec}_vmaf.sql"):
            episodePath = self.dashboard.fileSystem.getFile(f"processed/{self.jobPath}/{self.jobCodecEpisodeName}")
            self.jobSubprocess = subprocess.Popen([f"../scripts/ffmpeg-vmaf.sh", self.dashboard.fileSystem.getFile(self.jobSrcPath), episodePath], stdin=DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        self.runProgress()
        self.endSection()

        self.jobName = f"Transcoding job for '{self.jobPath}'"
        self.dashboard.fileSystem.freeFile(f"processed/{self.jobPath}/episode_x264.mp4")
        self.dashboard.fileSystem.freeFile(f"processed/{self.jobPath}/episode_vp9.webm")
        self.dashboard.fileSystem.freeFile(self.jobSrcPath, False)
        DEVNULL.close()