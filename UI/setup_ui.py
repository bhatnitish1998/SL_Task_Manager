from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QIcon
from .task_manager_ui import Ui_main_window
from Data.get_all_data import SystemInfo


class TaskManagerWindow(QWidget, Ui_main_window):
    def __init__(self):
        super().__init__()

        # set UI and icon
        self.setupUi(self)
        self.setWindowIcon(QIcon("../Media/icon.png"))

        # system info
        self.system_info = SystemInfo()
