from PyQt6.QtCore import QTimer

from PyQt6.QtGui import QIcon, QFont
import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QApplication, QTableWidgetItem, QLabel, QProgressBar, QHeaderView, QHBoxLayout, \
    QVBoxLayout
from task_manager_ui import Ui_main_window
import sys
from Data.get_resource_info import MemoryInfo
from Data.get_all_data import SystemInfo
from Data.network_data import NetworkInfo


class TaskManagerWindow(QWidget, Ui_main_window):
    def __init__(self):
        super().__init__()

        # set UI and icon
        self.setupUi(self)
        self.setWindowIcon(QIcon("../Media/icon.png"))

        # system info
        self.system_info = SystemInfo()
        self.set_cpu_info()
        self.number_of_cores = self.system_info.cpu_cores

        # set timer for update
        self.proc_timer = QTimer()
        self.proc_timer.setInterval(1000)
        self.proc_timer.timeout.connect(self.update_process_table)
        self.proc_timer.start()

        # set timer for update
        self.cpu_interval = 1000
        self.cpu_timer = QTimer()
        self.cpu_timer.setInterval(self.cpu_interval)
        self.cpu_timer.timeout.connect(self.update_cpu_info)
        self.cpu_timer.start()

        # set network timer
        self.network_interval = 500
        self.network_timer = QTimer()
        self.network_timer.setInterval(self.network_interval)
        self.network_timer.timeout.connect(self.update_network_info)
        self.network_timer.timeout.connect(self.update_interface_info)
        self.network_timer.start()


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

        self.core_x = [i for i in range(self.number_of_cores)]
        self.core_y = [0] * self.number_of_cores
        self.bar_graph = pg.BarGraphItem(x=self.core_x, height=self.core_y, width=0.5, brush='g')
        self.core_graph.getPlotItem().getAxis('bottom').setTicks([[(i, str(i)) for i in self.core_x]])
        self.core_graph.setYRange(0, 100)
        self.core_graph.setLabel('left', "Utilization % ")
        self.core_graph.setLabel('bottom', "CPU Cores")

        # overall cpu graph
        self.cpu_overall_graph = pg.PlotWidget()
        self.hbox_overall_cpu.addWidget(self.cpu_overall_graph)
        self.cpu_overall_graph.setLabel('left', "Utilization % ")
        self.cpu_overall_graph.setLabel('bottom', "Time in seconds")
        self.cpu_overall_graph.setYRange(0, 100)
        self.cpu_graph_x = [i / 1000 for i in range(-50 * self.cpu_interval, 1, self.cpu_interval)]
        self.cpu_graph_y = [0 for i in range(51)]
        pen = pg.mkPen(color=(0, 255, 0), width=5)
        self.cpu_line = self.cpu_overall_graph.plot(self.cpu_graph_x, self.cpu_graph_y, pen=pen)


        # network transmit graph
        self.network_transmit_graph = pg.PlotWidget()
        self.hbox_transmit_graph.addWidget(self.network_transmit_graph)
        self.network_transmit_graph.setLabel('left', "Transmit rate (KBps)")
        self.network_transmit_graph.setLabel('bottom', "Time in seconds")
        pen = pg.mkPen(color=(0, 255, 0), width=5)
        self.network_transmit_x = [i / 1000 for i in range(-50 * self.network_interval, 1, self.network_interval)]
        self.network_transmit_y =[0 for i in range(51)]
        self.network_transmit_line = self.network_transmit_graph.plot(self.network_transmit_x,self.network_transmit_y,pen=pen)

        # network receive graph
        self.network_receive_graph = pg.PlotWidget()
        self.hbox_receive_graph.addWidget(self.network_receive_graph)
        self.network_receive_graph.setLabel('left', "Receive rate (KBps)")
        self.network_receive_graph.setLabel('bottom', "Time in seconds")
        pen = pg.mkPen(color=(0, 255, 0), width=5)
        self.network_receive_x = [i / 1000 for i in range(-50 * self.network_interval, 1, self.network_interval)]
        self.network_receive_y =[0 for i in range(51)]
        self.network_receive_line = self.network_receive_graph.plot(self.network_receive_x,self.network_receive_y,pen=pen)

        # add interface info
        nw = NetworkInfo()
        data = nw.network_info
        cols = ["Interface", "IP", "MAC", "Send", "Receive"]
        vbox_t = []
        for i in range(len(cols)):
            vbox_t.append(QVBoxLayout())
            label = QLabel()
            label.setText(cols[i])
            font = QFont("Ubuntu", 12)
            font.setBold(True)
            label.setFont(font)
            vbox_t[i].addWidget(label)

        self.send_labels=[]
        self.receive_labels=[]
        for row in data:
            for i in range(len(row)):
                label = QLabel()
                label.setText(row[i])
                vbox_t[i].addWidget(label)
                if i == 3:
                    self.send_labels.append((label))
                if i ==4:
                    self.receive_labels.append(label)


        for i in range(len(vbox_t)):
            self.hbox_interfaces.addLayout(vbox_t[i])

        # add  diskinfo
        data = self.system_info.get_disk_data()
        for i in data.keys():
            label_disk_iter = QLabel()
            disk_str = f"{i}: {data[i] / (1024 * 1024)} GB"
            label_disk_iter.setText(disk_str)
            label_disk_iter.setFont(QFont("Ubuntu", 15))
            self.hbox_disk_info.addWidget(label_disk_iter)

        # add filesystem info
        # self.vbox_file_system.addWidget()
        data = self.system_info.fs_info
        cols = ["File-system", "Used", "Available", "Percent Used"]
        vbox_t = []
        for i  in range(len(cols)):
            vbox_t.append(QVBoxLayout())
            label = QLabel()
            label.setText(cols[i])
            font = QFont("Ubuntu",12)
            font.setBold(True)
            label.setFont(font)
            vbox_t[i].addWidget(label)

        for row in data:
            for i in range(len(row)):
                if i ==3:
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


    def update_interface_info(self):
        nw = NetworkInfo()
        data = nw.network_info
        for i in range(len(data)):
            for j in [3,4]:
                if j == 3:
                    self.send_labels[i].setText(data[i][j])
                if j ==4:
                    self.receive_labels[i].setText(data[i][j])

    def update_cpu_info(self):
        data = self.system_info.get_cpu_data()

        # update overall graph
        self.cpu_graph_x.pop(0)
        self.cpu_graph_x.append(self.cpu_graph_x[-1] + (self.cpu_interval / 1000))
        self.cpu_graph_y.pop(0)
        self.cpu_graph_y.append(data['cpu']['usage'])
        self.cpu_line.setData(self.cpu_graph_x, self.cpu_graph_y)

        # update core info
        self.core_y = [data[f'cpu{i}']['usage'] for i in range(self.number_of_cores)]
        self.core_graph.removeItem(self.bar_graph)
        self.bar_graph = pg.BarGraphItem(x=self.core_x, height=self.core_y, width=0.5, brush='g')
        self.core_graph.addItem(self.bar_graph)

    def set_cpu_info(self):
        data = self.system_info.cpu_meta
        self.label_cpu_model.setText(data["Model name"])
        self.label_core_info.setText("Core info")
        self.label_cache_info.setText("Cache info")
        self.label_l1_i_cache.setText(data['l1i_cache'])
        self.label_l1_d_cache.setText(data['l1d_cache'])
        self.label_l2_cache.setText(data['l2_cache'])
        self.label_l3_cache.setText(data['l3_cache'])
        self.label_cores.setText(data['cores'])
        self.label_threads_per_core.setText(data['threads'])
        self.label_max_cpu_speed.setText(data['max_cpu_freq'])

    def update_memory_info(self):
        # {total,available,used,free,s_total,s_used,s_free}
        memory = MemoryInfo()
        data = memory.get_memory_usage()
        div_factor = 1024 * 1024

        # update memory label
        used = data["used"] / div_factor
        total = data["total"] / div_factor
        used_percent = (used / total) * 100
        mem_string = f"{used:2.2f} GB ({used_percent:2.1f}%) of {total:2.2f} GB"
        self.label_mem_usage.setText(mem_string)

        # update swap label
        s_total = data["s_total"] / div_factor
        if s_total != 0:
            s_used = data["s_used"] / div_factor
            s_used_percent = (s_used / s_total) * 100
            swap_string = f"{s_used:2.2f} GB ({s_used_percent:2.1f}%) of {s_total:2.2f} GB"
        else:
            swap_string = "Unavailable"
        self.label_swap_usage.setText(swap_string)

        # update graph
        self.mem_graph_x.pop(0)
        self.mem_graph_x.append(self.mem_graph_x[-1] + (self.mem_interval / 1000))
        self.mem_graph_y.pop(0)
        self.mem_graph_y.append(used)
        self.mem_line.setData(self.mem_graph_x, self.mem_graph_y)

    def update_network_info(self):
        # update transmit graph
        data = self.system_info.get_network_data()
        transmit = data['total']['tx_KBps']
        receive = data['total']['rx_KBps']
        self.network_transmit_x.pop(0)
        self.network_transmit_x.append(self.network_transmit_x[-1] + (self.network_interval / 1000))
        self.network_transmit_y.pop(0)
        self.network_transmit_y.append(transmit)
        self.network_transmit_line.setData(self.network_transmit_x,self.network_transmit_y)


        # update receive graph
        self.network_receive_x.pop(0)
        self.network_receive_x.append(self.network_receive_x[-1] + (self.network_interval / 1000))
        self.network_receive_y.pop(0)
        self.network_receive_y.append(receive)
        self.network_receive_line.setData(self.network_receive_x,self.network_receive_y)


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
