import os

units = { "B": 1, "K": 10**3, "M": 10**6, "G": 10**9, "T": 10**12 }
def parseSize(size):
    number = size[:len(size)-1]
    unit = size[len(size)-1:]
    return int(float(number) * units[unit])

class NyanFilesystem():
    def __init__(self):
        self.basePath = "/usr/src/nyananime"
        self.mountPath = self.basePath
        self.ram = False
        self.ramUsed = 0
        self.ramSize = 0

        tmpfs_size = os.getenv("NYANANIME_TMPFS_SIZE")
        if tmpfs_size != None:
            self.mountPath = "/mnt/nyananime"
            self.ram = True
            self.ramSize = parseSize(tmpfs_size)
            if os.path.exists(self.mountPath):
                os.system(f'umount -f "{self.mountPath}"')
            os.system("modprobe zram num_devices=1")
            os.system(f"echo {tmpfs_size} > /sys/block/zram0/disksize")
            os.system(f"echo 0 > /sys/block/zram0/mem_limit")
            os.system(f'mkfs.ext4 /dev/zram0 && mount /dev/zram0 "{self.mountPath}"')

    def getFile(self, filePath):
        baseFilePath = f"{self.basePath}/{filePath}"
        mountFilePath = f"{self.mountPath}/{filePath}"
        if self.ram and not os.path.exists(mountFilePath) and os.path.exists(baseFilePath):
            baseFileStats = os.stat(baseFilePath)
            if self.ramUsed + baseFileStats.st_size < self.ramSize:
                os.system(f'mkdir -p {os.path.dirname(mountFilePath)} && cp "{baseFilePath}" "{mountFilePath}"')
                self.ramUsed += baseFileStats.st_size
                # print(f"Cached {filePath} of size {baseFileStats.st_size} (used: {self.ramUsed})...")
            else:
                return baseFilePath

        return mountFilePath

    def freeFile(self, filePath, move=True):
        baseFilePath = f"{self.basePath}/{filePath}"
        mountFilePath = f"{self.mountPath}/{filePath}"
        if self.ram and os.path.exists(mountFilePath):
            mountFileStats = os.stat(mountFilePath)
            if move and not os.path.exists(baseFilePath):
                os.system(f'mkdir -p {os.path.dirname(baseFilePath)} && mv "{mountFilePath}" "{baseFilePath}"')
            else:
                os.system(f'rm "{mountFilePath}"')
                self.ramUsed -= mountFileStats.st_size
            # print(f"Freed {filePath} of size {mountFileStats.st_size} (used: {self.ramUsed})...")
        
        return
