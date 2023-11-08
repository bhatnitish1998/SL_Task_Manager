from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget, QApplication, QTableWidgetItem
from task_manager_ui import Ui_main_window
import sys
from Data.proc_data import ProcessesData



class TaskManagerWindow(QWidget, Ui_main_window):
    def __init__(self):
        super().__init__()

        # set UI and icon
        self.setupUi(self)
        self.setWindowIcon(QIcon("../Media/icon.png"))

        # set timer for update
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_process_table)
        self.timer.start()

        # end task button
        self.button_endtask.clicked.connect(self.end_task)

    def end_task(self):
        current = self.table_processes.currentRow()
        print(current)

    def update_process_table(self):
        process = ProcessesData()
        data = process.get_data()
        # #data = [["root", "1", "process", "2", "running", "0.2%", "50 MB", "11:15", "11:35"],
        #         ["root", "1", "process", "2", "running", "0.2%", "50 MB", "11:15", "11:35"],
        #         ["root", "1", "process", "2", "running", "0.2%", "50 MB", "11:15", "11:35"], ]
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
