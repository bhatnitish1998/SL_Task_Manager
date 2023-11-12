import sys
from PyQt6.QtWidgets import QApplication
from memory_tab import MemoryTab
from cpu_tab import CPUTab
from network_tab import NetWorkTab
from process_tab import ProcessTab

class TaskManagerApp(MemoryTab,CPUTab,NetWorkTab,ProcessTab):
    def __init__(self):
        super().__init__()


app = QApplication(sys.argv)
main_window = TaskManagerApp()
main_window.show()
sys.exit(app.exec())