from PySide6.QtWidgets import QTableView

from csv_vaql_browser.csv_ui.csv_data_frame import CSVDataFrameModel


class CSVTableView(QTableView):
    def __init__(self, parent, table_model: CSVDataFrameModel):
        super().__init__(parent)
        self.table_model = table_model

        self.horizontalHeader().setVisible(True)
        self.setModel(table_model)
        self.resizeColumnsToContent = True
