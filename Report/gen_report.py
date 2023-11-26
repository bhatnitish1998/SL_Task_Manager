import math
import time
import subprocess
import os
from PyQt6.QtCore import QTimer
from typing import List, Dict, Any, Union
from datetime import datetime
from matplotlib import pyplot as plt

from Data.get_all_data import SystemInfo
from Data.utility_functions import kb_to_print


class ReportTemplate:
    def __init__(self, data, path) -> None:
        self.data = data
        self.path = path
        os.system(f"mkdir -p {self.path}")
        os.system(f"rm -rf {self.path}/*.png")

    def plot(self, cpu_data, ram_data, x_axis, index):
        # Plot CPU usage
        cpu_plt = plt
        cpu_plt.figure(figsize=(12, 6))  # Set the figure size to be wider
        cpu_plt.plot(x_axis, cpu_data, label="cpu usage")
        cpu_plt.xlabel("Timestamp")
        cpu_plt.ylabel("CPU Usage")
        cpu_plt.title("CPU Usage Over Time")
        cpu_plt.legend()
        # cpu_plt.xticks(rotation=30)  # Rotate x-axis tick labels
        cpu_plt.savefig(f"{self.path}/cpu_usage_{index}.png")
        cpu_plt.close()

        # Plot RAM usage
        ram_plt = plt
        ram_plt.figure(figsize=(12, 6))  # Set the figure size to be wider
        ram_plt.plot(x_axis, ram_data, label="ram usage")
        ram_plt.xlabel("Timestamp")
        ram_plt.ylabel("RAM Usage")
        ram_plt.title("RAM Usage Over Time")
        ram_plt.legend()
        # ram_plt.xticks(rotation=30)  # Rotate x-axis tick labels
        ram_plt.savefig(f"{self.path}/ram_usage_{index}.png")
        ram_plt.close()

    def do_plots(self):
        cpu_data = [x.cpu_usage for x in self.data["stats"]]
        ram_usage = [x.ram_usage for x in self.data["stats"]]
        timestamp = [idx+1 for idx in range(len(self.data["stats"]))]
        for i in range(0, len(self.data["stats"]), 100):
            self.plot(cpu_data[i:i+100], ram_usage[i:i+100],
                      timestamp[i:i+100], i//100+1)

    def render_static_data(self):
        template = """
        \\section{System Info}
        \\textbf{{{Model name}}}\\\\\\\\
        \\textbf{Core info}\\\\
        Number of cores: {{cores}}\\\\
        Threads per core: {{threads}}\\\\
        Max Cpu frequency: {{max_cpu_freq}}\\\\\\\\
        \\textbf{Cache info}\\\\
        L1 Instruction cache: {{l1i_cache}}\\\\
        L1 Data Cache: {{l1d_cache}} \\\\
        L2 Cache: {{l2_cache}}\\\\
        L3 Cache: {{l3_cache}}\\\\\\\\
        \\textbf{Memory info}\\\\
        Total RAM: {{total}}\\\\
        Total Swap: {{s_total}}\\\\\\\\
        """
        output = template
        for variable, value in self.data["cpu_info"].items():
            output = output.replace("{{" + variable + "}}", value)
        for variable, value in self.data["ram_info"].items():
            # print(value, type(value))
            if variable not in output:
                continue
            output = output.replace("{{" + variable + "}}", kb_to_print(value))

        with open(f"{self.path}/sys_info.tex", "w") as f:
            f.writelines(output)

    def render_log_data(self):
        log_template = '''
        {timestamp} & {cpu_usage}  & {ram_usage} \\\\
        '''
        lines = []
        lines.append(log_template.format(timestamp="timestamp",
                                         cpu_usage="cpu usage",
                                         ram_usage="ram usage"))
        for data in self.data["stats"]:
            formatted_timestamp = datetime.fromtimestamp(
                data.timestamp).strftime("%H:%M:%S")
            lines.append(
                log_template.format(timestamp=formatted_timestamp,
                                    cpu_usage=data.cpu_usage,
                                    ram_usage=data.ram_usage))
        with open(f"{self.path}/log.tex", "w") as f:
            f.writelines(lines)

    def render_plots(self):
        template = """
        \\section{Resource Utilization Graphs}

        \\textbf{CPU Utilization}
        {{cpugraphs}}


        \\textbf{Memory Utilization}
        {{ramgraphs}}
        """

        template_graph = """
        \\begin{figure}[h!]
            \\centering
            \\includegraphics[height = 200 pt, width = 350pt]{{{cpugraph.png}}}
        \\end{figure}
        """
        cpu_graphs = ""
        ram_graphs = ""
        self.do_plots()
        for file in os.listdir(self.path):
            if file.endswith(".png"):
                # print(file)
                output = template_graph.replace("{{cpugraph.png}}", file)
                if "cpu" in file:
                    cpu_graphs += output
                elif "ram" in file:
                    ram_graphs += output
        output = template.replace("{{cpugraphs}}", cpu_graphs)
        output = output.replace("{{ramgraphs}}", ram_graphs)
        with open(f"{self.path}/graph.tex", "w") as f:
            f.writelines(output)

    def gen_pdf(self, output: str):
        subprocess.run(
            "cd Report && pdflatex main.tex > /dev/null", shell=True)

    def prepare_render(self):
        self.render_static_data()
        self.render_log_data()
        self.render_plots()

    def render(self, output: str = "report.pdf"):
        self.gen_pdf(output=output)


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
                 csv_file: str = "./report.pdf"
                 ) -> None:
        self.system_info = SystemInfo()

        self.data: Dict[str, Union[List[ReportData], Dict]] = {
            "stats": [],
            "cpu_info": {},
            "ram_info": {},
        }

        self.csv_file = csv_file

        self.max_samples = math.ceil(period/interval)

        self._get_static_data()
        # self.time = threading.Timer(interval, self.add_data).start()
        self.timers = []
        self.report_template = ReportTemplate(
            self.data, "Report/")
        self._timer(interval, self._add_data)
        self._timer(period, self.generate_report)

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
        self.data["ram_info"] = self.system_info.get_mem_data()

    def _add_data(self):
        timestamp = time.time()
        cpu_usage = self.system_info.get_cpu_data()
        ram_usage = self.system_info.get_mem_data()
        self.data["stats"].append(ReportData(timestamp, cpu_usage, ram_usage))

        self.data["stats"] = self.data["stats"]

    def generate_report(self):
        self.report_template.prepare_render()
        # self.report_template.render(output=self.csv_file)

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

    def __del__(self):
        self.report_template.render(output=self.csv_file)
