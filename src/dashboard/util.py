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

def getColor(color):
    colors = {
        "gray": "\033[0;37m",
        "bright_blue": "\033[0;94m",
        "bright_green": "\033[0;92m",
        "reset": "\033[0m"
    }
    return colors.get(color)


def getFiles(id):
    system(f"mkdir -p /usr/src/nyananime/src-episodes/{id}")
    system(f"mkdir -p /usr/src/nyananime/dest-episodes/{id}")
    src_files = subprocess.getoutput(f"find -L /usr/src/nyananime/src-episodes/{id} -name *.mkv | wc -l")
    dest_files = subprocess.getoutput(f"find /usr/src/nyananime/dest-episodes/{id} -name *.mkv | wc -l")
    return { "src_files": src_files, "dest_files": dest_files }