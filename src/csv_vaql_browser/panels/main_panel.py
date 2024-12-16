import time
from pathlib import Path
from queue import Queue
from threading import Thread

from PySide6.QtCore import QMargins, Qt, Signal
from PySide6.QtWidgets import QVBoxLayout, QMenu, QWidget, QProgressDialog

from csv_vaql_browser.app_context import AppContext
from csv_vaql_browser.csv_ui import CSVDataFrameModel, CSVTableView
from csv_vaql_browser.tools.err import msg_on_err
from csv_vaql_browser.tools.panel_widget import Panel
from csv_vaql_browser.tools.recenetly_opened_files import update_last_opened_files_menu
from csv_vaql_browser.tools.thread_messages import EXIT


class MainPanel(Panel[QVBoxLayout]):
    load_dialog_signal = Signal((int,))
    load_csv_signal = Signal((str,))

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
            self, table_model = CSVDataFrameModel(
                ctx = ctx, on_load = on_csv_load, on_change = on_filter_change, main_win = dialogs_parent
            )
        )
        self.layout().addWidget(self.table_view)

        # connect to context
        table_model = self.table_view.table_model
        self.load_csv_signal.connect(table_model.load_csv_file)


        ctx.load_csv_file = lambda file_name: self.load_csv_signal.emit(file_name)
        # ctx.load_csv_file = lambda file_name: msg_on_err(table_model.load_csv_file(file_name), dialogs_parent)
        ctx.save_csv_file = lambda file_name: msg_on_err(table_model.save_csv_file(file_name), dialogs_parent)
        ctx.enable_substring_filter = table_model.enable_substring_filter
        ctx.enable_sql_filter = table_model.enable_sql_filter
        ctx.apply_filter = table_model.apply_filter
        ctx.filter_on_vaql = table_model.filter_on_vaql

        self.progress_control_queue = Queue[EXIT]()
        ctx.register_queue_for_exit(self.progress_control_queue)

    def load_progress_dialog(self) -> QProgressDialog:
        return self.progress

    def update_load_progress_dialog(self, new_value: int):
        print(f"t = {time.time()} :: {new_value}")
        self.progress.setValue(new_value)

    def show_load_progress_dialog2(self):
        self.progress = QProgressDialog("Loading csv file", "Abort", 0, 100, self)
        self.dq = self.load_dialog_signal.connect(self.progress.setValue, Qt.ConnectionType.DirectConnection)

        self.progress.setValue(0)
        self.progress.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress.show()

        def upd():
            i = 0
            while i < 10:
                self.progress.setValue(i)
                time.sleep(0.1)
                i += 1

        Thread(target = upd).start()

        # def foo():
        #     while True:
        #         try:
        #             cmd = self.progress_control_queue.get_nowait()
        #             if cmd is EXIT:
        #                 return
        #         except Empty:
        #             pass
        #         time.sleep(0.2)
        #         orig_value = self.progress.value()
        #         print(f"orig_value = {orig_value}")
        #         new_value = int((orig_value + 1) % 100)
        #         print(f"new_value = {new_value}")
        #         self.load_dialog_signal.emit(new_value)
        #
        # self.progress_dialog_updater = Thread(target = foo)
        # self.progress_dialog_updater.start()

    def close_load_progress_dialog2(self):
        self.progress.disconnect(self.dq)
        self.progress_control_queue.put(EXIT)
        self.progress.close()
