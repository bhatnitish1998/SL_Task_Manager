from PyQt6.QtWidgets import QWidget, QApplication, QTableWidgetItem, QLabel, QProgressBar, QVBoxLayout
from PyQt6.QtCore import QTimer

from setup_ui import TaskManagerWindow
class ProcessTab(TaskManagerWindow):
    def __init__(self):
        super().__init__()

        # set process update timer
        self.proc_timer = QTimer()
        self.proc_timer.setInterval(1000)
        self.proc_timer.timeout.connect(self.update_process_table)
        self.proc_timer.start()

        # end task button
        self.button_endtask.clicked.connect(self.end_task)

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

