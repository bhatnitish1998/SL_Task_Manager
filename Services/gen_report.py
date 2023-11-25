# TODO
# 1. data structure for storing the report
# 2. report template
# 3. write data to report template with raw data and graphs
# 4. report template to

from Data.get_all_data import SystemInfo
import math
import time
from PyQt6.QtCore import QTimer
from typing import List, Dict, Any, Union


class ReportTemplate:
    def __init__(self, data) -> None:
        self.data = data
        self.write_to_template()

    def write_to_template(self):
        pass

    def save_pdf(self, path):
        pass


class ReportData:
    def __init__(self, timestamp, cpu_usage, ram_usage) -> None:
        self.timestamp = timestamp
        self.cpu_usage = cpu_usage["cpu"]["usage"]
        self.ram_usage = ram_usage["used_percent"]


class Report:
    """
    Attributes:
        data (Dict["stats", Union[List[ReportData], Dict[str, Any]]])
    """

    def __init__(self,
                 interval: int = 10,
                 period: int = 15*60,
                 csv_file: str = "report.csv"
                 ) -> None:
        self.system_info = SystemInfo()

        self.data: Dict[str, Union[List[ReportData], Dict]] = {
            "stats": [],
            "cpu_info": {},
        }

        self.csv_file = csv_file

        self.max_samples = math.ceil(period/interval)

        self._get_static_data()
        # self.time = threading.Timer(interval, self.add_data).start()
        self.timers = []
        self._timer(interval, self._add_data)
        self._timer(interval+5, self.save_csv)

    def _timer(self, interval, fn):
        """
        Helper function to create a timer
        Args:
            interval (int): interval in seconds
            fn (function): function to be called
        """
        new_timers = QTimer()
        new_timers.setInterval(interval*1000)
        new_timers.timeout.connect(fn)
        new_timers.start()
        self.timers.append(new_timers)

    def _get_static_data(self):
        self.data["cpu_info"] = self.system_info.cpu_meta

    def _add_data(self):
        timestamp = time.time()
        cpu_usage = self.system_info.get_cpu_data()
        ram_usage = self.system_info.get_mem_data()
        self.data["stats"].append(ReportData(timestamp, cpu_usage, ram_usage))

        self.data["stats"] = self.data["stats"]

    def generate_report(self):
        pass

    def save_csv(self, csv_file: str = None):
        """
        Save data to csv file
        Args:
            csv_file (str, optional): csv file path. Defaults to ./reports.csv.
        """
        if not csv_file:
            csv_file = self.csv_file
        lines = ["timestamp, cpu_usage, ram_usage, network_usage\n"]
        for data in self.data["stats"]:
            lines.append(
                f"{data.timestamp}, {data.cpu_usage}, {data.ram_usage}\n")
        with open(csv_file, "w") as f:
            f.writelines(lines)


if __name__ == "__main__":
    report = Report(interval=1, period=10)
    k = 0
    while k <= 100:
        time.sleep(1)
        k = k+1
    report.save_csv()
    # report.generate_report()
