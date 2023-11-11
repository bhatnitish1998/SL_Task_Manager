# This file contains the CPUInfo class that provides information about CPU usage.
import os
import time


class CPUInfo:
    """
    A class that provides information about CPU usage.

    Attributes:
        cpu_headers (List[str]): A list of strings representing the headers of the CPU data.
        prev_cpu_stats (Dict[str, Dict[str, int]]): A dictionary containing the previous CPU stats.
        proc_stat_fd (TextIOWrapper): A file descriptor for reading the /proc/stat file.

    Methods:
        _get_proc_stat(): Reads the /proc/stat file and returns its contents as a string.
        _read_cpu_stats(): Parses the CPU data from /proc/stat and returns a dictionary with the CPU usage stats.
        get_cpu_usage(): Returns a dictionary with the CPU usage percentage for each CPU.
    """

    def __init__(self):
        self.proc_stat_fd = self._get_proc_stat_fd()
        self.cpu_headers = ['user', 'nice', 'system',
                            'idle', 'iowait', 'irq', 'softirq',]
        self.prev_cpu_stats = self._init_cpu_stats()
        self.number_cores = self._get_cpu_cores()
        self.prev_cpu_usage = {}
        self.cpu_meta = self._get_cpu_meta()

    def _get_proc_stat_fd(self):
        return open('/proc/stat', 'r')

    def _get_proc_stat(self):
        self.proc_stat_fd.seek(0)
        return self.proc_stat_fd.read()

    def _init_cpu_stats(self):
        cpu_data = self._read_cpu_stats()
        for core, data in cpu_data.items():
            cpu_data[core]["total_jiffies"] = 0
            cpu_data[core]["work_jiffies"] = 0
        return cpu_data

    def _read_cpu_stats(self):
        data = self._get_proc_stat()
        data_rows = data.split('\n')
        cpu_data = {}
        for data_row in data_rows:
            if data_row.startswith('cpu'):
                _cpu_data = data_row.split()
                _cpu_type = _cpu_data[0]
                _cpu_raw_data = [int(data) for data in _cpu_data[1:]]
                _cpu_data = {self.cpu_headers[idx]: _cpu_raw_data[idx]
                             for idx in range(len(self.cpu_headers))}
                # cpu_data[_cpu_type] = _cpu_data
                cpu_data[_cpu_type] = {}
                cpu_data[_cpu_type]["total_jiffies"] = sum(_cpu_data.values())
                cpu_data[_cpu_type]["work_jiffies"] = sum(
                    [_cpu_data["user"], _cpu_data["nice"], _cpu_data["system"]]
                )

        return cpu_data

    def _get_cpu_cores(self):
        return len(self.prev_cpu_stats.keys()) - 1

    def get_cpu_usage(self):
        current_cpu_stats = self._read_cpu_stats()
        cpu_usage = {}
        for item in current_cpu_stats.items():
            cpu = item[0]
            cpu_usage[cpu] = {}
            total_over_period = (
                current_cpu_stats[cpu]["total_jiffies"] -
                self.prev_cpu_stats[cpu]["total_jiffies"]
            )
            work_over_period = (
                current_cpu_stats[cpu]["work_jiffies"] -
                self.prev_cpu_stats[cpu]["work_jiffies"]
            )
            if total_over_period == 0:
                cpu_usage[cpu] = self.prev_cpu_usage[cpu]
            else:
                cpu_usage[cpu]["usage"] = round((
                    work_over_period /
                    total_over_period
                ) * 100, 1)
        self.prev_cpu_stats = current_cpu_stats
        self.prev_cpu_usage = cpu_usage
        return cpu_usage

    def _get_cpu_meta(self):
        cpu_info = os.popen("lscpu").read()
        cpu_meta = {}
        for line in cpu_info.split("\n"):
            if line == "":
                continue
            key, value = line.split(":")[:2]
            key = key.strip()
            value = value.strip()
            cpu_meta[key] = value

        return cpu_meta


if __name__ == "__main__":
    cpu_info = CPUInfo()
    print(cpu_info.cpu_meta)
    while True:
        time.sleep(1)  # Wait for a while to measure the change in CPU usage
        cpu_usage = cpu_info.get_cpu_usage()

        print("CPU Usage:")
        for cpu_core, cpu_usage in cpu_usage.items():
            print(f'{cpu_core}: {cpu_usage["usage"]}%')
