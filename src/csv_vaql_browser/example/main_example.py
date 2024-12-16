import sys

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QApplication, QProgressDialog


class W(QMainWindow):
    s = Signal()

    def __init__(self):
        super().__init__()

        root_panel = QWidget()
        layout = QVBoxLayout()
        root_panel.setLayout(layout)
        self.button = QPushButton("Start a process")
        layout.addWidget(self.button)
        self.s.connect(self.show_pdialog)
        self.button.clicked.connect(self.show_pdialog)
        self.setCentralWidget(root_panel)

    def show_pdialog(self) -> None:
        print("Hello")
        progress_dialog = QProgressDialog("Loading csv file", "Abort", 0, 100, self)
        # self.dq = self.load_dialog_signal.connect(self.progress.setValue, Qt.ConnectionType.DirectConnection)

        progress_dialog.setMinimumDuration(0)
        progress_dialog.setValue(3)
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        progress_dialog.show()

        def update():
            # print("update ...")
            new_value = int((progress_dialog.value() + 1) % 100)
            progress_dialog.setValue(new_value)

        t = QTimer(self)
        t.timeout.connect(update)
        t.start(100)

        progress_dialog.canceled.connect(t.stop)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = W()
    win.show()
    # win.show_pdialog()
    # win.button.click()
    win.s.emit()
    sys.exit(app.exec())
