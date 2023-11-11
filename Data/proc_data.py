import os
import datetime
import pwd

class ProcessInfo:
    '''
    Class to parse proc file and gather stats about the processes
    Available attributes:
    name
    threads
    state
    cpu_usage
    mem_usage
    start_time
    running_time
    # TODO: issues: runningtime: -ve, start_time: only time, cpu,mem: round to 2 decimal places
    '''

    def __init__(self, pid) -> None:
        self.proc_path = '/proc'
        self.pid = pid
        self.user = self.get_process_user()
        self.stat_fd = open(os.path.join(self.proc_path, str(self.pid), 'stat'), 'r')
        self.update_stats()

    def update_stats(self,):
        self.stat_fd.seek(0)
        self.stat_raw = self.stat_fd.read()
    
    def get_stats(self):
        return self.stat_raw
    
    def get_process_user(self):
        try:
            # Get the stat information of the process directory
            stat = os.stat(f"/proc/{self.pid}")
            
            # Get the user ID and group ID of the owner
            uid = stat.st_uid
            gid = stat.st_gid
            
            # Look up the username and group name using the user and group IDs
            username = pwd.getpwuid(uid).pw_name
            # groupname = os.getgrgid(gid).gr_name
            
            return username
        except (FileNotFoundError, KeyError):
            return None
    
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
        cpu_usage = 100.0 * ((total_time / hertz) / seconds)
        return round(cpu_usage, 2)

    @property
    def mem_usage(self):
        statm_path = os.path.join(self.proc_path, str(self.pid), 'statm')
        with open(statm_path, 'r') as statm_file:
            statm_info = statm_file.read().split()
            resident_set_size = int(statm_info[1]) * os.sysconf(os.sysconf_names['SC_PAGE_SIZE']) / (1024 * 1024)  # in MB
            return round(resident_set_size, 2)

    @property
    def start_time(self):
        starttime = int(self.get_process_start_time())
        return datetime.datetime.fromtimestamp(starttime)

    @property
    def running_time(self):
        start_time = self.get_process_start_time()
        now = datetime.datetime.now().timestamp()
        return round(now - start_time, 2)

    def get_uptime(self):
        with open(os.path.join(self.proc_path, 'uptime')) as uptime_file:
            uptime = float(uptime_file.read().split()[0])
            return uptime

    def get_process_start_time(self):
        stat_data = self.get_stats()
        starttime = int(stat_data.split(" ")[21])
        hertz = os.sysconf(os.sysconf_names['SC_CLK_TCK'])
        uptime = self.get_uptime()
        start_time_seconds = datetime.datetime.now().timestamp() - (uptime - starttime/hertz)
        return start_time_seconds
    
    def get_data(self):
        try:
            self.update_stats()
        except FileNotFoundError:
            return None
        except ProcessLookupError:
            return None
        
        return [
            self.user,
            self.pid,
            self.name,
            self.state,
            self.threads,
            self.cpu_usage,
            self.mem_usage,
            self.start_time,
            self.running_time
        ]

    def __del__(self):
        print(f"Deleting processInfo obj {self.pid}")
        try:
            self.stat_fd.close()
        except FileNotFoundError:
            pass

    def __dict__(self):
        self.update_stats()
        return {
            "pid": self.pid,
            "user": self.user,
            "name": self.name,
            "threads": self.threads,
            "state": self.state,
            "cpu_usage": self.cpu_usage,
            "mem_usage": self.mem_usage,
            "start_time": self.start_time,
            "running_time": self.running_time
        }

    def __repr__(self):
        self.update_stats()
        return f"ProcessInfo(pid={self.pid}, name={self.name}, uid={self.user}, threads={self.threads}, state={self.state}, cpu_usage={self.cpu_usage:.2f}%, mem_usage={self.mem_usage:.2f} MB, start_time={self.start_time}, running_time={self.running_time:.2f} seconds)"

    def __str__(self):
        self.update_stats()
        return f"Process ID: {self.pid}\nProcess Name: {self.name}\nUID: {self.user}\nThreads: {self.threads}\nState: {self.state}\nCPU Usage: {self.cpu_usage:.2f}%\nMemory Usage: {self.mem_usage:.2f} MB\nStart Time: {self.start_time}\nRunning Time: {self.running_time:.2f} seconds"


class ProcessesData:
    '''
    Class to parse proc file and gather stats about the processes
    '''
    def __init__(self) -> None:
        self.proc_path = '/proc'
        self.cache = {}
        self._get_process_info()

    def _get_process_info(self):
        '''
        Get the process info for all processes
        '''
        new_cache = {}
        for pid in os.listdir(self.proc_path):
            if pid.isdigit():  # Process directories are named with digits
                try:
                    if pid in self.cache:
                        new_cache[pid] = self.cache[pid]
                    else:
                        pid_info = ProcessInfo(pid)
                        new_cache[pid] = pid_info
                except FileNotFoundError:
                    pass
        return new_cache
    
    def get_processes(self):
        self.cache = self._get_process_info()
        return [process for process in self.cache.values()]
    
    def get_data(self):
        self.processes = self.get_processes()
        data = [process.get_data() for process in self.processes]
        return [process_data for process_data in data if process_data is not None]
