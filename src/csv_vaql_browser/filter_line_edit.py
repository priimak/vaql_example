from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QLineEdit


class FilterLineEdit(QLineEdit):
    def keyPressEvent(self, event: QKeyEvent):
        """
        Clear filter input form when Escape is pressed. Otherwise, propagate
        key press events to the parent class.
        """
        match event.key():
            case Qt.Key.Key_Escape:
                self.clear()
            case _:
                super().keyPressEvent(event)
