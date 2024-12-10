from typing import Type, override

from PySide6.QtWidgets import QWidget, QLayout, QSpacerItem


class Panel[T: QLayout](QWidget):
    def __init__(self, layout: T, widgets: list[QWidget | Type[QSpacerItem]] | None = None):
        super().__init__()
        self.setLayout(layout)

        if widgets is not None:
            for w in widgets:
                if w is QSpacerItem:
                    layout.addStretch(1)
                else:
                    layout.addWidget(w)

    @override
    def layout(self) -> T:
        return super().layout()
