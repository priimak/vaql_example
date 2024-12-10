from PySide6.QtWidgets import QLabel, QHBoxLayout

from csv_vaql_browser.app_context import AppContext
from csv_vaql_browser.tools.panel_widget import Panel


class BottomPanel(Panel[QHBoxLayout]):
    def __init__(self, ctx: AppContext):
        super().__init__(QHBoxLayout())
        self.opened_file_label = QLabel("")
        self.csv_dimensions_label = QLabel("")

        self.layout().addWidget(self.opened_file_label)
        self.layout().addStretch(stretch = 1)
        self.layout().addWidget(self.csv_dimensions_label)

        # connect dispatching methods in AppContext to relevant functions
        ctx.set_opened_file_label_text = self.opened_file_label.setText
        ctx.set_csv_dimensions_label_text = self.csv_dimensions_label.setText
