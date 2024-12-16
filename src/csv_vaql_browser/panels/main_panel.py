from pathlib import Path
from queue import Queue

from PySide6.QtCore import QMargins, Signal
from PySide6.QtWidgets import QVBoxLayout, QMenu, QWidget

from csv_vaql_browser.app_context import AppContext
from csv_vaql_browser.csv_ui import CSVDataFrameModel, CSVTableView
from csv_vaql_browser.tools.err import msg_on_err
from csv_vaql_browser.tools.panel_widget import Panel
from csv_vaql_browser.tools.recenetly_opened_files import update_last_opened_files_menu
from csv_vaql_browser.tools.thread_messages import EXIT


class MainPanel(Panel[QVBoxLayout]):
    upd_last_opened_files_menu_signal = Signal(str)

    def __init__(self, ctx: AppContext, recently_opened_files_menu: QMenu, dialogs_parent: QWidget):
        super().__init__(QVBoxLayout())
        self.layout().setContentsMargins(QMargins(0, 0, 0, 0))

        self.ctx = ctx
        self.recently_opened_files_menu = recently_opened_files_menu

        self.upd_last_opened_files_menu_signal.connect(self.upd_last_opened_files_menu)

        def on_csv_load(file_name: str, table_model: CSVDataFrameModel):
            ctx.app_persistence.state.save_value("last_opened_dir", Path(file_name).parent.absolute())
            ctx.set_opened_file_label_text(f"{Path(file_name).absolute()}")
            table_model.layoutChanged.emit()
            ctx.set_csv_dimensions_label_text(f"{table_model.csv.shape[0]} x {table_model.columnCount()}")
            self.table_view.resizeColumnsToContents()

            self.upd_last_opened_files_menu_signal.emit(file_name)

        def on_filter_change(table_model: CSVDataFrameModel):
            table_model.layoutChanged.emit()
            ctx.set_csv_dimensions_label_text(f"{table_model.csv.shape[0]} x {table_model.columnCount()}")

        self.table_view: CSVTableView = CSVTableView(
            self, table_model = CSVDataFrameModel(
                ctx = ctx, on_load = on_csv_load, on_change = on_filter_change, main_win = dialogs_parent
            )
        )
        self.layout().addWidget(self.table_view)

        # connect to context
        table_model = self.table_view.table_model
        ctx.load_csv_file = self.table_view.table_model.load_csv_file

        # ctx.load_csv_file = lambda file_name: msg_on_err(table_model.load_csv_file(file_name), dialogs_parent)
        ctx.save_csv_file = lambda file_name: msg_on_err(table_model.save_csv_file(file_name), dialogs_parent)
        ctx.enable_substring_filter = table_model.enable_substring_filter
        ctx.enable_sql_filter = table_model.enable_sql_filter
        ctx.apply_filter = table_model.apply_filter
        ctx.filter_on_vaql = table_model.filter_on_vaql

        self.progress_control_queue = Queue[EXIT]()
        ctx.register_queue_for_exit(self.progress_control_queue)

    def upd_last_opened_files_menu(self, file_name: str):
        update_last_opened_files_menu(
            app_persistence = self.ctx.app_persistence,
            recently_opened_menu = self.recently_opened_files_menu,
            file_name = file_name,
            ctx = self.ctx
        )
