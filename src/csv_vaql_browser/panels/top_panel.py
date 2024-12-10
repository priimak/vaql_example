from PySide6.QtCore import QMargins
from PySide6.QtWidgets import QComboBox, QHBoxLayout

from csv_vaql_browser.app_context import AppContext
from csv_vaql_browser.filter_line_edit import FilterLineEdit
from csv_vaql_browser.tools.panel_widget import Panel

class TopPanel(Panel[QHBoxLayout]):
    def __init__(self, ctx: AppContext):
        super().__init__(QHBoxLayout())
        self.layout.setContentsMargins(QMargins(1, 1, 1, 5))

        self.filter_line_edit = FilterLineEdit()
        self.saved_filter_line_edit_text = ""

        self.filter_line_edit.textChanged.connect(lambda: ctx.apply_filter(self.filter_line_edit.text()))
        self.layout.addWidget(self.filter_line_edit)
