from Data.get_resource_info import DiskInfo, MemoryInfo
from Data.proc_data import ProcessesData
from Data.network_data import NetworkInfo
from Data.cpu_data import CPUInfo


class SystemInfo:
    """
    A class that provides information about system resources.
    Attributes:
        processes_data (ProcessesData): An instance of the ProcessesData class.
        network_data (NetworkInfo): An instance of the NetworkInfo class.
        disk_info (DiskInfo): An instance of the DiskInfo class.
        memory_info (MemoryInfo): An instance of the MemoryInfo class.
    Methods:
        get_process_data(): Returns a list of dictionaries with information about running processes.
        get_mem_data(): Returns a dictionary with information about memory usage.
        get_disk_data(): Returns a dictionary with information about disk usage.
        get_network_data(): Returns a dictionary with information about network usage.
    """

    def __init__(self, exclude_interfaces: list = []) -> None:
        self.processes_data = ProcessesData()
        self.network_data = NetworkInfo(exclude_interfaces=exclude_interfaces)
        self.disk_info = DiskInfo()
        self.memory_info = MemoryInfo()

        self.cpu_info = CPUInfo()
        self.cpu_meta = self.cpu_info.cpu_meta
        self.cpu_cores = self.cpu_info.number_cores
        self.fs_info = self.disk_info.get_fs_info()

    def get_process_data(self,):
        return self.processes_data.get_data()

    def get_mem_data(self):
        return self.memory_info.get_memory_usage()

    def get_disk_data(self):
        return self.disk_info.get_disk_usage()

    def get_network_data(self):
        return self.network_data.get_network_usage()

    def get_cpu_data(self):
        return self.cpu_info.get_cpu_usage()
