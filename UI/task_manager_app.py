from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QIcon
import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QApplication, QTableWidgetItem
from task_manager_ui import Ui_main_window
import sys
from Data.get_resource_info import MemoryInfo
from Data.get_all_data import SystemInfo
from Data.cpu_data import CPUInfo
import random


class TaskManagerWindow(QWidget, Ui_main_window):
    def __init__(self):
        super().__init__()

        # set UI and icon
        self.setupUi(self)
        self.setWindowIcon(QIcon("../Media/icon.png"))

        # system info
        self.system_info = SystemInfo()

        # set timer for update
        self.proc_timer = QTimer()
        self.proc_timer.setInterval(1000)
        self.proc_timer.timeout.connect(self.update_process_table)
        self.proc_timer.start()

        # set timer for update
        self.cpu_interval = 1000
        self.cpu_timer = QTimer()
        self.cpu_timer.setInterval(self.cpu_interval)
        self.cpu_timer.timeout.connect(self.update_core_info)
        self.cpu_timer.timeout.connect(self.update_cpu_overall)
        self.cpu_timer.start()

        # set memory timer for update
        self.mem_interval = 500
        self.mem_timer = QTimer()
        self.mem_timer.setInterval(self.mem_interval)
        self.mem_timer.timeout.connect(self.update_memory_info)
        self.mem_timer.start()

        # end task button
        self.button_endtask.clicked.connect(self.end_task)

        # memory graph
        self.mem_usage_graph = pg.PlotWidget()
        self.hbox_mem_graph.addWidget(self.mem_usage_graph)
        self.mem_graph_x = [i / 1000 for i in range(-50 * self.mem_interval, 1, self.mem_interval)]
        self.mem_graph_y = [0 for i in range(51)]
        pen = pg.mkPen(color=(0, 255, 0), width=5)
        self.mem_line = self.mem_usage_graph.plot(self.mem_graph_x, self.mem_graph_y, pen=pen)
        self.mem_usage_graph.setLabel('left', "Memory Used (GB)")
        self.mem_usage_graph.setLabel('bottom', "Time elapsed (seconds)")
        memory = MemoryInfo()
        data = memory.get_memory_usage()
        self.mem_usage_graph.setYRange(0, data["total"] / (1024 * 1024))

        # core graph
        self.core_graph = pg.PlotWidget()
        self.hbox_core_graph.addWidget(self.core_graph)
        self.number_of_core = 24
        self.core_x = [i for i in range(self.number_of_core)]
        core_y = [random.randint(0, 100) for i in range(self.number_of_core)]
        self.bar_graph = pg.BarGraphItem(x=self.core_x, height=core_y, width=0.5, brush='g')
        self.core_graph.getPlotItem().getAxis('bottom').setTicks([[(i,str(i) )for i in self.core_x]])
        self.core_graph.setYRange(0,100)
        self.core_graph.setLabel('left', "Utilization % ")
        self.core_graph.setLabel('bottom', "CPU Cores")

        # overall cpu graph
        self.cpu_overall_graph = pg.PlotWidget()
        self.hbox_overall_cpu.addWidget(self.cpu_overall_graph)
        self.cpu_overall_x = []
        self.cpu_overall_graph.setLabel('left', "Utilization % ")
        self.cpu_overall_graph.setLabel('bottom', "Time in seconds")
        self.cpu_overall_graph.setYRange(0, 100)

        self.cpu_graph_x = [i / 1000 for i in range(-50 * self.cpu_interval, 1, self.cpu_interval)]
        self.cpu_graph_y = [0 for i in range(51)]
        pen = pg.mkPen(color=(0, 255, 0), width=5)
        self.cpu_line = self.cpu_overall_graph.plot(self.cpu_graph_x, self.cpu_graph_y, pen=pen)

    def update_cpu_overall(self):
        self.cpu_graph_x.pop(0)
        self.cpu_graph_x.append(self.cpu_graph_x[-1] + (self.cpu_interval / 1000))
        self.cpu_graph_y.pop(0)
        r = random.randint(0,100)
        self.cpu_graph_y.append(r)
        self.cpu_line.setData(self.cpu_graph_x, self.cpu_graph_y)


    def update_core_info(self):
        # cpu = CPUInfo()
        # data = cpu.get_cpu_usage()
        # print(cpu)
        core_y = [random.randint(0, 100) for i in range(self.number_of_core)]
        self.core_graph.removeItem(self.bar_graph)
        self.bar_graph = pg.BarGraphItem(x=self.core_x, height=core_y, width=0.5, brush='g')
        self.core_graph.addItem(self.bar_graph)

    def update_memory_info(self):
        # {total,available,used,free,s_total,s_used,s_free}
        memory = MemoryInfo()
        data = memory.get_memory_usage()
        div_factor = 1024 * 1024

        # update memory label
        used = data["used"] / div_factor
        total = data["total"] / div_factor
        used_percent = (used / total) * 100
        mem_string = f"Memory : {used:2.2f} GB ({used_percent:2.1f}%) of {total:2.2f} GB"
        self.label_mem_usage.setText(mem_string)

        # update swap label
        s_used = data["s_used"] / div_factor
        s_total = data["s_total"] / div_factor
        s_used_percent = (s_used / s_total) * 100
        swap_string = f"Swap: {s_used:2.2f} GB ({s_used_percent:2.1f}%) of {s_total:2.2f} GB"
        self.label_swap_usage.setText(swap_string)

        # update graph
        self.mem_graph_x.pop(0)
        self.mem_graph_x.append(self.mem_graph_x[-1] + (self.mem_interval / 1000))
        self.mem_graph_y.pop(0)
        self.mem_graph_y.append(used)
        self.mem_line.setData(self.mem_graph_x, self.mem_graph_y)

    def end_task(self):
        current = self.table_processes.currentRow()
        print(current)

    def update_process_table(self):
        # gets list of lists of all processes
        data = self.system_info.get_process_data()
        n_row = len(data)
        n_col = 9
        self.table_processes.setRowCount(n_row)
        self.table_processes.setColumnCount(n_col)

        for row in range(n_row):
            for column in range(n_col):
                my_item = QTableWidgetItem(str(data[row][column]))
                my_item.setTextAlignment(4)
                self.table_processes.setItem(row, column, my_item)


app = QApplication(sys.argv)
main_window = TaskManagerWindow()
main_window.show()
sys.exit(app.exec())
