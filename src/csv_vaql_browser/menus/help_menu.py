from PySide6.QtWidgets import QMenu, QMenuBar, QMessageBox, QWidget


class HelpMenu(QMenu):
    def __init__(self, parent: QMenuBar, about_dialog_parent: QWidget):
        super().__init__("&Help", parent)
        self.addAction("&About", lambda: QMessageBox.about(about_dialog_parent, "About", "CSV Browser App"))
