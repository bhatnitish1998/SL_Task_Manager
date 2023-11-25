import subprocess
from Data.utility_functions import kb_to_print


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
        self.div_factor = 1024 * 1024

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

        # memory label string and percent
        used = self.used / self.div_factor
        total = self.total / self.div_factor
        used_percent = (used / total) * 100
        mem_string = f"{used:2.2f} GB ({used_percent:2.1f}%) of {total:2.2f} GB"

        s_used_percent = 0
        # swap label string and percent
        if self.swap_total != 0:
            s_total = self.swap_total / self.div_factor
            s_used = self.swap_used / self.div_factor
            s_used_percent = (s_used / s_total) * 100
            swap_string = f"{s_used:2.2f} GB ({s_used_percent:2.1f}%) of {s_total:2.2f} GB"
        else:
            swap_string = "Unavailable"

        return {"total": self.total, "free": self.free, "available": self.available, "used": self.used,
                "s_total": self.swap_total, "s_free": self.swap_free, "s_used": self.swap_used,
                "used_percent": round(used_percent, 2), "s_used_percent": round(s_used_percent, 2),
                "mem_string": mem_string,
                "swap_string": swap_string}


class DiskInfo:
    def __init__(self):
        self.number_of_disks = 0
        # dictionary key = name value = [total capacity ,used ,available for linux]
        self.disk_data = {}
        self.fs_data = []

    def get_meta_info(self):
        result = subprocess.run(["lsblk | grep disk"], shell=True, capture_output=True, text=True).stdout.strip().split(
            '\n')
        for line in result:
            row = line.split()
            self.disk_data[row[0]] = (float(row[3][:-1]) * (2 ** 20))
        self.number_of_disks = len(self.disk_data.keys())

    def get_fs_info(self):
        self.fs_data.clear()
        result = subprocess.run(
            ["df"], shell=True, capture_output=True, text=True).stdout.strip().split('\n')[1:]
        for line in result:
            row = line.split()
            if (row[0] != 'tmpfs'):
                used = kb_to_print(int(row[2]))
                available = kb_to_print(int(row[3]))
                # used = f'{int(row[2])/(1024*1024):.2f} GB'
                # available = f'{int(row[3])/(1024*1024):.2f} GB'
                self.fs_data.append([row[0], used, available, row[4][:-1]])
                # self.fs_data[row[0]]={}
                # self.fs_data[row[0]]["used"]=int(row[2])
                # self.fs_data[row[0]]["available"] =int(row[3])
                # self.fs_data[row[0]]["use_percent"] =int(row[4][:-1])
        return self.fs_data

    def get_disk_usage(self):
        self.get_meta_info()
        return self.disk_data


if __name__ == "__main__":
    d = DiskInfo()
    d.get_fs_info()
