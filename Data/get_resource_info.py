# all attributes are in kb right now
class MemoryInfo:
    def __init__(self):
        self.total =0
        self.free =0
        self.available =0
        self.used =0
        self.swap_total =0
        self.swap_free =0
        self.swap_used =0

    def update_meminfo(self):
        with open("/proc/meminfo","r") as myfile:
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