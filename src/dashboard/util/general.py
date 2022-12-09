import time, threading, subprocess
from os import system

class setInterval :
    def __init__(self,interval,action) :
        self.interval=interval
        self.action=action
        self.stopEvent=threading.Event()
        thread=threading.Thread(target=self.__setInterval)
        thread.start()

    def __setInterval(self) :
        nextTime=time.time()+self.interval
        while not self.stopEvent.wait(nextTime-time.time()) :
            nextTime+=self.interval
            self.action()

    def cancel(self) :
        self.stopEvent.set()

def colorize(color, text):
    colors = {
        "gray": "\033[0;37m",
        "bright_blue": "\033[0;94m",
        "bright_green": "\033[0;92m",
        "yellow": "\033[0;33m",
        "white": "\033[0;37m",
        "reset": "\033[0m"
    }
    return f"{colors[color]}{text}{colors['reset']}"


def getFiles(id):
    system(f"mkdir -p /usr/src/nyananime/source/{id}")
    system(f"mkdir -p /usr/src/nyananime/processed/{id}")
    src_files = subprocess.getoutput(f"find -L /usr/src/nyananime/source/{id} -name *.mkv | wc -l")
    dest_files = subprocess.getoutput(f"find /usr/src/nyananime/processed/{id} -name *.mp4 | wc -l")
    return { "src_files": src_files, "dest_files": dest_files }