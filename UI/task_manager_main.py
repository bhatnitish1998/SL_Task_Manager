import sys
from PyQt6.QtWidgets import QApplication
from .memory_tab import MemoryTab
from .cpu_tab import CPUTab
from .network_tab import NetWorkTab
from .process_tab import ProcessTab

from Report.gen_report import Report


class TaskManagerApp(MemoryTab, CPUTab, NetWorkTab, ProcessTab):
    def __init__(self):
        super().__init__()
        self.report = Report(interval=1, period=5)


app = QApplication(sys.argv)
main_window = TaskManagerApp()
main_window.show()
sys.exit(app.exec())
