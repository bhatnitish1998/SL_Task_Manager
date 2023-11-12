
import pyqtgraph as pg
from PyQt6.QtWidgets import QLabel, QVBoxLayout
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import  QFont
from Data.network_data import NetworkInfo

from setup_ui import TaskManagerWindow
class NetWorkTab(TaskManagerWindow):
    def __init__(self):
        super().__init__()

        # set network update timer
        self.network_interval = 500
        self.network_timer = QTimer()
        self.network_timer.setInterval(self.network_interval)
        self.network_timer.timeout.connect(self.update_network_info)
        self.network_timer.timeout.connect(self.update_interface_info)
        self.network_timer.start()

        # network transmit graph
        self.network_transmit_graph = pg.PlotWidget()
        self.hbox_transmit_graph.addWidget(self.network_transmit_graph)
        self.network_transmit_graph.setLabel('left', "Transmit rate (KBps)")
        self.network_transmit_graph.setLabel('bottom', "Time in seconds")
        pen = pg.mkPen(color=(0, 255, 0), width=5)
        self.network_transmit_x = [i / 1000 for i in range(-50 * self.network_interval, 1, self.network_interval)]
        self.network_transmit_y = [0 for i in range(51)]
        self.network_transmit_line = self.network_transmit_graph.plot(self.network_transmit_x, self.network_transmit_y,
                                                                      pen=pen)

        # network receive graph
        self.network_receive_graph = pg.PlotWidget()
        self.hbox_receive_graph.addWidget(self.network_receive_graph)
        self.network_receive_graph.setLabel('left', "Receive rate (KBps)")
        self.network_receive_graph.setLabel('bottom', "Time in seconds")
        pen = pg.mkPen(color=(0, 255, 0), width=5)
        self.network_receive_x = [i / 1000 for i in range(-50 * self.network_interval, 1, self.network_interval)]
        self.network_receive_y = [0 for i in range(51)]
        self.network_receive_line = self.network_receive_graph.plot(self.network_receive_x, self.network_receive_y,
                                                                    pen=pen)

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

        self.send_labels = []
        self.receive_labels = []
        for row in data:
            for i in range(len(row)):
                label = QLabel()
                label.setText(row[i])
                vbox_t[i].addWidget(label)
                if i == 3:
                    self.send_labels.append((label))
                if i == 4:
                    self.receive_labels.append(label)

        for i in range(len(vbox_t)):
            self.hbox_interfaces.addLayout(vbox_t[i])

    def update_network_info(self):
        # update transmit graph
        data = self.system_info.get_network_data()
        transmit = data['total']['tx_KBps']
        receive = data['total']['rx_KBps']
        self.network_transmit_x.pop(0)
        self.network_transmit_x.append(self.network_transmit_x[-1] + (self.network_interval / 1000))
        self.network_transmit_y.pop(0)
        self.network_transmit_y.append(transmit)
        self.network_transmit_line.setData(self.network_transmit_x, self.network_transmit_y)

        # update receive graph
        self.network_receive_x.pop(0)
        self.network_receive_x.append(self.network_receive_x[-1] + (self.network_interval / 1000))
        self.network_receive_y.pop(0)
        self.network_receive_y.append(receive)
        self.network_receive_line.setData(self.network_receive_x, self.network_receive_y)

    def update_interface_info(self):
        nw = NetworkInfo()
        data = nw.network_info
        for i in range(len(data)):
            for j in [3, 4]:
                if j == 3:
                    self.send_labels[i].setText(data[i][j])
                if j == 4:
                    self.receive_labels[i].setText(data[i][j])
