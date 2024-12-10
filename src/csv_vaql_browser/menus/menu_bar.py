from PySide6.QtWidgets import QMenuBar, QWidget

from csv_vaql_browser.app_context import AppContext
from csv_vaql_browser.menus import FileMenu, HelpMenu


class MainMenuBar(QMenuBar):
    def __init__(self, ctx: AppContext, dialogs_parent: QWidget):
        super().__init__(None)

        self.file_menu = FileMenu(self, ctx, dialogs_parent)
        self.addMenu(self.file_menu)
        self.addMenu(HelpMenu(self, dialogs_parent))
