from PyQt6.QtWidgets import QTableWidgetItem, QMessageBox
from PyQt6.QtCore import QTimer

import subprocess
from collections import defaultdict

from setup_ui import TaskManagerWindow


class NumericTableWidgetItem(QTableWidgetItem):
    """
    To hold int and float data of table cell for custom sorting
    """

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

        # set notification timer
        self.notify_interval = 60000
        self.notify_timer = QTimer()
        self.notify_timer.setInterval(self.notify_interval)
        self.notify_timer.timeout.connect(self.set_flag_true)

        # notify flag and level
        self.notify_flag = True
        self.notify_level = 100
        self.threshold_breach = defaultdict(lambda: 0)

    def set_flag_true(self):
        self.notify_flag = True
        self.notify_timer.stop()

    def end_task(self):
        selected_row = self.table_processes.selectedItems()[0].row()
        selected_item = self.table_processes.item(selected_row, 1)
        pid = selected_item.text()
        result = subprocess.run(["kill", pid])
        if result.returncode == 0:
            QMessageBox.information(self, "Success", "Process terminated successfully")
        else:
            QMessageBox.warning(self, "Permission Denied", "You do not have required permissions for this task")

    def update_process_table(self):
        # gets list of lists of all processes
        data = self.system_info.get_process_data()
        n_row = len(data)
        n_col = 9
        self.table_processes.setRowCount(n_row)
        self.table_processes.setColumnCount(n_col)

        # update individual cell of table
        for row in range(n_row):
            for column in range(n_col):
                value = data[row][column]

                # check max resource usage
                if column == 4 and value >= self.notify_level:
                    self.notify(data[row])

                # create numerical object if int/float
                if isinstance(value, (int, float)):
                    my_item = NumericTableWidgetItem(value)
                else:
                    my_item = QTableWidgetItem(str(value))

                my_item.setTextAlignment(4)
                self.table_processes.setItem(row, column, my_item)

    def notify(self, row):
        pid = row[1]

        self.threshold_breach[pid] += 1
        if self.threshold_breach[pid] == 5:
            self.threshold_breach[pid] = 0
            if self.notify_flag:
                pname = row[8]
                cmd = f'notify-send "Process {pname} with pid {pid} is using too much resources"'
                subprocess.run(cmd, shell=True)
                self.notify_flag = False
                self.notify_timer.start()
