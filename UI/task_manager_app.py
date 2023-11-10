from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QIcon
import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QApplication, QTableWidgetItem
from task_manager_ui import Ui_main_window
import sys
from Data.proc_data import ProcessesData
from Data.get_resource_info import MemoryInfo


class TaskManagerWindow(QWidget, Ui_main_window):
    def __init__(self):
        super().__init__()

        # set UI and icon
        self.setupUi(self)
        self.setWindowIcon(QIcon("../Media/icon.png"))

        # set timer for update
        self.proc_timer = QTimer()
        self.proc_timer.setInterval(1000)
        self.proc_timer.timeout.connect(self.update_process_table)
        self.proc_timer.start()

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
        self.mem_graph_x = [i/1000 for i in range(-50*self.mem_interval,1,self.mem_interval)]
        self.mem_graph_y = [0 for i in range(51)]
        pen = pg.mkPen(color=(0, 255, 0),width=5)
        self.mem_line = self.mem_usage_graph.plot(self.mem_graph_x, self.mem_graph_y, pen=pen)
        self.mem_usage_graph.setLabel('left',"Memory Used (GB)")
        self.mem_usage_graph.setLabel('bottom', "Time elapsed (seconds)")
        memory = MemoryInfo()
        data = memory.return_meminfo()
        self.mem_usage_graph.setYRange(0,data["total"]/(1024*1024))


    def update_memory_info(self):
        # {total,available,used,free,s_total,s_used,s_free}
        memory = MemoryInfo()
        data = memory.return_meminfo()
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

        #update graph
        self.mem_graph_x.pop(0)
        self.mem_graph_x.append(self.mem_graph_x[-1] + (self.mem_interval/1000))
        self.mem_graph_y.pop(0)
        self.mem_graph_y.append(used)
        self.mem_line.setData(self.mem_graph_x, self.mem_graph_y)

    def end_task(self):
        current = self.table_processes.currentRow()
        print(current)

    def update_process_table(self):
        process = ProcessesData()
        data = process.get_data()
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
