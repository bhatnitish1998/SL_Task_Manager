import os
import datetime

class ProcessInfo:
    '''
    Class to parse proc file and gather stats about the processes
    '''

    def __init__(self, pid) -> None:
        self.proc_path = '/proc'
        self.pid = pid
        self.stat_fd = open(os.path.join(self.proc_path, str(self.pid), 'stat'), 'r')
        self.update_stats()
    
    def update_stats(self,):
        self.stat_fd.seek(0)
        self.stat_raw = self.stat_fd.read()
    
    def get_stats(self):
        return self.stat_raw
    
    @property
    def name(self):
        stat_data = self.get_stats()
        return stat_data.split(" ")[1][1:-1]

    @property
    def threads(self):
        stat_data = self.get_stats()
        return int(stat_data.split(" ")[19])

    @property
    def state(self):
        stat_data = self.get_stats()
        return stat_data.split(" ")[2]

    @property
    def cpu_usage(self):
        stat_data = self.get_stats()
        utime = int(stat_data.split(" ")[13])
        stime = int(stat_data.split(" ")[14])
        starttime = int(stat_data.split(" ")[21])
        hertz = os.sysconf(os.sysconf_names['SC_CLK_TCK'])
        total_time = utime + stime
        uptime = os.sysconf(os.sysconf_names['SC_CLK_TCK']) * self.get_uptime()
        seconds = uptime - (starttime / hertz)
        return 100.0 * ((total_time / hertz) / seconds)

    @property
    def mem_usage(self):
        statm_path = os.path.join(self.proc_path, str(self.pid), 'statm')
        with open(statm_path, 'r') as statm_file:
            statm_info = statm_file.read().split()
            resident_set_size = int(statm_info[1]) * os.sysconf(os.sysconf_names['SC_PAGE_SIZE']) / (1024 * 1024)  # in MB
            return resident_set_size

    @property
    def start_time(self):
        starttime = int(self.get_process_start_time())
        return datetime.datetime.fromtimestamp(starttime)

    @property
    def running_time(self):
        start_time = self.get_process_start_time()
        now = datetime.datetime.now().timestamp()
        return now - start_time

    def get_uptime(self):
        with open(os.path.join(self.proc_path, 'uptime')) as uptime_file:
            uptime = float(uptime_file.read().split()[0])
            return uptime

    def get_process_start_time(self):
        stat_data = self.get_stats()
        starttime = int(stat_data.split(" ")[21])
        hertz = os.sysconf(os.sysconf_names['SC_CLK_TCK'])
        uptime = self.get_uptime()
        start_time_seconds = datetime.datetime.now().timestamp() - (starttime - uptime)
        return start_time_seconds

    def __del__(self):
        self.stat_fd.close()

    def __dict__(self):
        return {
            "name": self.name,
            "threads": self.threads,
            "state": self.state,
            "cpu_usage": self.cpu_usage,
            "mem_usage": self.mem_usage,
            "start_time": self.start_time,
            "running_time": self.running_time
        }

    def __repr__(self):
        return f"ProcessInfo(pid={self.pid}, name={self.name}, threads={self.threads}, state={self.state}, cpu_usage={self.cpu_usage:.2f}%, mem_usage={self.mem_usage:.2f} MB, start_time={self.start_time}, running_time={self.running_time:.2f} seconds)"

    def __str__(self):
        return f"Process ID: {self.pid}\nProcess Name: {self.name}\nThreads: {self.threads}\nState: {self.state}\nCPU Usage: {self.cpu_usage:.2f}%\nMemory Usage: {self.mem_usage:.2f} MB\nStart Time: {self.start_time}\nRunning Time: {self.running_time:.2f} seconds"


class ProcessesData:
    '''
    Class to parse proc file and gather stats about the processes
    '''
    def __init__(self) -> None:
        self.proc_path = '/proc'
        self.processes = self.get_process_info()

    def get_process_info(self):
        '''
        Get the process info for all processes
        '''
        process_info = []
        for pid in os.listdir(self.proc_path):
            if pid.isdigit():  # Process directories are named with digits
                try:
                    pid_info = ProcessInfo(pid)
                    process_info.append(pid_info)
                except FileNotFoundError:
                    # Ignore processes that may have exited between listing and reading
                    pass
        return process_info



if __name__ == "__main__":
    processData = ProcessesData()
    for process in processData.processes[-5:]:
        print('-'*20)
        print(process)
        print('\n')
