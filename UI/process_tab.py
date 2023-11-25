from PyQt6.QtWidgets import QWidget, QApplication, QTableWidgetItem, QLabel, QProgressBar, QVBoxLayout
from PyQt6.QtCore import QTimer

from setup_ui import TaskManagerWindow

class NumericTableWidgetItem(QTableWidgetItem):
    def __init__(self, value):
        super().__init__(str(value))

    def __lt__(self, other):
        # Custom comparison for numerical values
        try:
            return float(self.text()) > float(other.text())

        except ValueError:
            return super().__lt__(other)



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
                value = data[row][column]
                if isinstance(value, (int, float)):
                    my_item = NumericTableWidgetItem(value)
                else:
                    my_item = QTableWidgetItem(str(value))

                my_item.setTextAlignment(4)
                self.table_processes.setItem(row, column, my_item)

