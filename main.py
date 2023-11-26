from PyQt6.QtWidgets import QApplication
from UI.task_manager_main import TaskManagerApp

app = QApplication(sys.argv)
main_window = TaskManagerApp()
main_window.show()
sys.exit(app.exec())
