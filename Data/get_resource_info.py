import subprocess


# all attributes are in kb right now
class MemoryInfo:
    def __init__(self):
        self.total = 0
        self.free = 0
        self.available = 0
        self.used = 0
        self.swap_total = 0
        self.swap_free = 0
        self.swap_used = 0

    def update_meminfo(self):
        with open("/proc/meminfo", "r") as myfile:
            for line in myfile:
                if "MemTotal" in line:
                    self.total = int(line.split()[1])
                if "MemFree" in line:
                    self.free = int(line.split()[1])
                if "MemAvailable" in line:
                    self.available = int(line.split()[1])
                if "SwapTotal" in line:
                    self.swap_total = int(line.split()[1])
                if "SwapFree" in line:
                    self.swap_free = int(line.split()[1])

        self.used = self.total - self.free
        self.swap_used = self.swap_total - self.swap_free

    def get_memory_usage(self):
        self.update_meminfo()
        return {"total": self.total, "free": self.free, "available": self.available, "used": self.used,
                "s_total": self.swap_total, "s_free": self.swap_free, "s_used": self.swap_used}


class DiskInfo:
    def __init__(self):
        self.number_of_disks = 0
        # dictionary key = name value = [total capacity ,used ,available for linux]
        self.disk_data = {}

    def get_meta_info(self):
        result = subprocess.run(["lsblk | grep disk"], shell=True, capture_output=True, text=True).stdout.strip().split(
            '\n')
        for line in result:
            row = line.split()
            self.disk_data[row[0]] = [0, 0, 0]
            self.disk_data[row[0]][0] = (float(row[3][:-1]) * (2 ** 20))

        self.number_of_disks = len(self.disk_data.keys())

    def update_diskinfo(self):
        result = subprocess.run(
            ["df"], shell=True, capture_output=True, text=True).stdout.strip().split('\n')
        for line in result:
            row = line.split()
            for key in self.disk_data.keys():
                if key in row[0]:
                    self.disk_data[key][1] = (int(row[2]))
                    self.disk_data[key][2] = (int(row[3]))



    def get_disk_usage(self):
        self.get_meta_info()
        return self.disk_data

if __name__ == "__main__":
    d = DiskInfo()
    d.update_diskinfo()