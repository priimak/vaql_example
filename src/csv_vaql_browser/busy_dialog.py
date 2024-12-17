from PySide6.QtCore import QTimer, Signal, Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QWidget, QLabel, QProgressBar


class BusyDialog(QDialog):
    close_request = Signal()

    def __init__(self, parent: QWidget, title: str, message: str):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle(title)
        self.close_request.connect(self.close)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint)

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel(message))
        progress_bar = QProgressBar(self)
        progress_bar.setTextVisible(False)
        progress_bar.setRange(0, 20)
        progress_bar.setValue(0)
        self.layout().addWidget(progress_bar)

        self.t = QTimer()
        self.t.setInterval(30)  # update every 30 ms
        self.t.timeout.connect(lambda: progress_bar.setValue((progress_bar.value() + 1) % 20))

    def show(self):
        super().show()
        self.t.start()

    def closeEvent(self, arg__1):
        self.t.stop()
        super().closeEvent(arg__1)
