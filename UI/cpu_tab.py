from PyQt6.QtCore import QTimer
import pyqtgraph as pg

from .setup_ui import TaskManagerWindow


class CPUTab(TaskManagerWindow):
    def __init__(self):
        super().__init__()

        # cpu info
        self.set_cpu_info()
        self.number_of_cores = self.system_info.cpu_cores

        # set cpu update timer
        self.cpu_interval = 500
        self.cpu_timer = QTimer()
        self.cpu_timer.setInterval(self.cpu_interval)
        self.cpu_timer.timeout.connect(self.update_cpu_info)
        self.cpu_timer.start()

        # core graph
        self.core_graph = pg.PlotWidget()
        self.hbox_core_graph.addWidget(self.core_graph)
        self.core_x = [i for i in range(self.number_of_cores)]
        self.core_y = [0] * self.number_of_cores
        self.bar_graph = pg.BarGraphItem(
            x=self.core_x, height=self.core_y, width=0.5, brush='g')
        self.core_graph.getPlotItem().getAxis('bottom').setTicks(
            [[(i, str(i)) for i in self.core_x]])
        self.core_graph.setYRange(0, 100)
        self.core_graph.setLabel('left', "Utilization % ")
        self.core_graph.setLabel('bottom', "CPU Cores")
        self.core_graph.setMouseEnabled(x=False, y=False)

        # overall cpu graph
        self.cpu_overall_graph = pg.PlotWidget()
        self.hbox_overall_cpu.addWidget(self.cpu_overall_graph)
        self.cpu_overall_graph.setLabel('left', "Utilization % ")
        self.cpu_overall_graph.setLabel('bottom', "Time in seconds")
        self.cpu_overall_graph.setYRange(0, 100)
        self.cpu_graph_x = [
            i / 1000 for i in range(-50 * self.cpu_interval, 1, self.cpu_interval)]
        self.cpu_graph_y = [0 for _ in range(51)]
        pen = pg.mkPen(color=(0, 255, 0), width=5)
        self.cpu_line = self.cpu_overall_graph.plot(
            self.cpu_graph_x, self.cpu_graph_y, pen=pen)
        self.cpu_overall_graph.setMouseEnabled(x=False, y=False)

    def update_cpu_info(self):
        data = self.system_info.get_cpu_data()

        # update overall graph
        self.cpu_graph_x.pop(0)
        self.cpu_graph_x.append(
            self.cpu_graph_x[-1] + (self.cpu_interval / 1000))
        self.cpu_graph_y.pop(0)
        self.cpu_graph_y.append(data['cpu']['usage'])
        self.cpu_line.setData(self.cpu_graph_x, self.cpu_graph_y)

        # update core info
        self.core_y = [data[f'cpu{i}']['usage']
                       for i in range(self.number_of_cores)]
        self.core_graph.removeItem(self.bar_graph)
        self.bar_graph = pg.BarGraphItem(
            x=self.core_x, height=self.core_y, width=0.5, brush='g')
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
