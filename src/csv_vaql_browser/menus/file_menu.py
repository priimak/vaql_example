from pathlib import Path

from PySide6.QtWidgets import QMenu, QFileDialog, QMenuBar, QMessageBox, QWidget

from csv_vaql_browser.app_context import AppContext
from csv_vaql_browser.settings_dialog import SettingsDialog
from csv_vaql_browser.tools.recenetly_opened_files import init_recently_opened_menu


class FileMenu(QMenu):
    def __init__(self, parent: QMenuBar, ctx: AppContext, dialogs_parent: QWidget):
        super().__init__("&File", parent)

        # Open - menu item
        def open_csv_file_prompt() -> None:
            last_opened_dir = ctx.app_persistence.state.get_value("last_opened_dir", f"{Path.home()}")
            file_name, _ = QFileDialog.getOpenFileName(
                self, caption = "Open CSV File", dir = last_opened_dir, filter = "*.csv"
            )
            if file_name != "":
                ctx.load_csv_file(file_name)

        self.addAction("&Open", open_csv_file_prompt)

        # Prev Opened - menu item
        self.recently_opened_menu = self.addMenu("&Prev Opened")
        init_recently_opened_menu(
            app_persistence = ctx.app_persistence,
            recently_opened_menu = self.recently_opened_menu,
            ctx = ctx
        )

        # Other menu items
        def save_file():
            result = QMessageBox.question(dialogs_parent, "Save file.", "Override opened file?")
            if result == QMessageBox.StandardButton.Yes:
                ctx.save_csv_file(None)

        def save_file_as():
            target_dir = ctx.app_persistence.state.get_value("last_opened_dir", f"{Path.home()}")
            target_file_name, _ = QFileDialog.getSaveFileName(
                parent = dialogs_parent,
                caption = "Save CSV File",
                dir = target_dir,
                filter = "*.csv"
            )

            if target_file_name != "":
                ctx.save_csv_file(target_file_name)

        self.addAction("&Save", save_file)
        self.addAction("Save &As", save_file_as)
        self.addSeparator()

        def show_settings():
            dialog = SettingsDialog(parent = dialogs_parent, app_config = ctx.app_persistence.config)
            dialog.show()

        self.addAction("Se&ttings", show_settings)

        self.addSeparator()
        self.addAction("&Quit", lambda: ctx.exit_application())
