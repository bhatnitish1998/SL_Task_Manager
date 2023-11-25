from PyQt6.QtWidgets import QLabel, QProgressBar, QVBoxLayout
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QFont
import pyqtgraph as pg

from setup_ui import TaskManagerWindow


class MemoryTab(TaskManagerWindow):
    def __init__(self):
        super().__init__()

        # set memory update timer
        self.mem_interval = 500
        self.mem_timer = QTimer()
        self.mem_timer.setInterval(self.mem_interval)
        self.mem_timer.timeout.connect(self.update_memory_info)
        self.mem_timer.start()

        # memory graph
        self.mem_usage_graph = pg.PlotWidget()
        self.hbox_mem_graph.addWidget(self.mem_usage_graph)
        self.mem_graph_x = [i / 1000 for i in range(-50 * self.mem_interval, 1, self.mem_interval)]
        self.mem_graph_y = [0 for _ in range(51)]
        pen = pg.mkPen(color=(0, 255, 0), width=5)
        self.mem_line = self.mem_usage_graph.plot(self.mem_graph_x, self.mem_graph_y, pen=pen)
        self.mem_usage_graph.setLabel('left', "Memory Used (GB)")
        self.mem_usage_graph.setLabel('bottom', "Time elapsed (seconds)")
        data = self.system_info.get_mem_data()
        self.mem_usage_graph.setYRange(0, data["total"] / (1024 * 1024))
        self.mem_usage_graph.setMouseEnabled(x=False, y=False)

        # add  diskinfo
        data = self.system_info.get_disk_data()
        for i in data.keys():
            label_disk_iter = QLabel()
            disk_str = f"{i}: {data[i] / (1024 * 1024)} GB"
            label_disk_iter.setText(disk_str)
            label_disk_iter.setFont(QFont("Ubuntu", 15))
            self.hbox_disk_info.addWidget(label_disk_iter)

        # add filesystem info
        data = self.system_info.fs_info
        cols = ["File-system", "Used", "Available", "Percent Used"]
        vbox_t = []
        for i in range(len(cols)):
            vbox_t.append(QVBoxLayout())
            label = QLabel()
            label.setText(cols[i])
            font = QFont("Ubuntu", 12)
            font.setBold(True)
            label.setFont(font)
            vbox_t[i].addWidget(label)

        for row in data:
            for i in range(len(row)):
                if i == 3:
                    progbar = QProgressBar()
                    progbar.setValue(int(row[i]))
                    progbar.setStyleSheet("QProgressBar {background-color: #00ff00; color:white;}"
                                          "QProgressBar::chunk{background-color: #000000; padding:50px}")
                    vbox_t[i].addWidget(progbar)
                else:
                    label = QLabel()
                    label.setText(row[i])
                    vbox_t[i].addWidget(label)

        for i in range(len(vbox_t)):
            self.hbox_file_system.addLayout(vbox_t[i])

    def update_memory_info(self):
        data = self.system_info.get_mem_data()
        div_factor = 1024 * 1024

        # update memory label use %
        used = data["used"] / div_factor
        self.label_mem_usage.setText(data["mem_string"])

        # update swap label use %
        self.label_swap_usage.setText(data["swap_string"])

        # update graph
        self.mem_graph_x.pop(0)
        self.mem_graph_x.append(self.mem_graph_x[-1] + (self.mem_interval / 1000))
        self.mem_graph_y.pop(0)
        self.mem_graph_y.append(used)
        self.mem_line.setData(self.mem_graph_x, self.mem_graph_y)
