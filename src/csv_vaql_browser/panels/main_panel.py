from pathlib import Path

from PySide6.QtCore import QMargins
from PySide6.QtWidgets import QVBoxLayout, QMenu, QWidget

from csv_vaql_browser.app_context import AppContext
from csv_vaql_browser.csv_ui import CSVDataFrameModel, CSVTableView
from csv_vaql_browser.tools.err import msg_on_err
from csv_vaql_browser.tools.panel_widget import Panel
from csv_vaql_browser.tools.recenetly_opened_files import update_last_opened_files_menu


class MainPanel(Panel[QVBoxLayout]):
    def __init__(self, ctx: AppContext, recently_opened_files_menu: QMenu, dialogs_parent: QWidget):
        super().__init__(QVBoxLayout())
        self.layout().setContentsMargins(QMargins(0, 0, 0, 0))

        self.ctx = ctx

        def on_csv_load(file_name: str, table_model: CSVDataFrameModel):
            ctx.app_persistence.state.save_value("last_opened_dir", Path(file_name).parent.absolute())
            ctx.upd_last_opened_files_menu(file_name, lambda file: (lambda: ctx.load_csv_file(f"{file}")))
            ctx.set_opened_file_label_text(f"{Path(file_name).absolute()}")
            table_model.layoutChanged.emit()
            ctx.set_csv_dimensions_label_text(f"{table_model.csv.shape[0]} x {table_model.columnCount()}")
            self.table_view.resizeColumnsToContents()

            update_last_opened_files_menu(
                app_persistence = ctx.app_persistence,
                recently_opened_menu = recently_opened_files_menu,
                file_name = file_name,
                file_opener_factory = lambda file: (lambda: ctx.load_csv_file(f"{file}"))
            )

        def on_filter_change(table_model: CSVDataFrameModel):
            table_model.layoutChanged.emit()
            ctx.set_csv_dimensions_label_text(f"{table_model.csv.shape[0]} x {table_model.columnCount()}")

        self.table_view: CSVTableView = CSVTableView(
            self, table_model = CSVDataFrameModel(on_load = on_csv_load, on_change = on_filter_change)
        )
        self.layout().addWidget(self.table_view)

        # connect to context
        table_model = self.table_view.table_model

        ctx.load_csv_file = lambda file_name: msg_on_err(table_model.load_csv_file(file_name), dialogs_parent)
        ctx.save_csv_file = lambda file_name: msg_on_err(table_model.save_csv_file(file_name), dialogs_parent)
        ctx.enable_substring_filter = table_model.enable_substring_filter
        ctx.enable_sql_filter = table_model.enable_sql_filter
        ctx.apply_filter = table_model.apply_filter
        ctx.filter_on_vaql = table_model.filter_on_vaql
